import sys
import json
import time
import secrets
import pathlib
import argparse
import tempfile
import webbrowser
from typing import Dict

import tqdm
import jinja2
import requests

from . import azure_cli
from . import github_cli
from . import radix_cli
from . import interactive_terminal
from .radix_configuration import radix_configuration
from .azure_configuration import azure_configuration


def create_radix_config(
    build_directory: pathlib.Path, settings: Dict[str, str]
) -> None:
    template_environment = jinja2.Environment(  # nosec
        loader=jinja2.PackageLoader("webviz_config", "templates"),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )
    template = template_environment.get_template("radixconfig.yaml.jinja2")

    (build_directory / "radixconfig.yaml").write_text(template.render(settings))
    (build_directory / "auth-state.Dockerfile").write_text(
        "FROM redis:alpine\nUSER 999"
    )


def website_online(url: str) -> bool:
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
    return True


def radix_initial_deployment(github_slug: str, build_directory: pathlib.Path) -> None:
    """Creates a Radix configuration file."""
    # pylint: disable=too-many-statements

    if not radix_cli.binary_available():
        raise RuntimeError(
            "The Radix CLI is not available in $PATH. If you haven't downloaded it, "
            "you can find binaries here: https://github.com/equinor/radix-cli/releases"
        )

    if not github_cli.binary_available():
        raise RuntimeError(
            "The GitHub CLI is not available in $PATH. If you haven't downloaded it, "
            "you can find binaries here: https://github.com/cli/cli/releases"
        )

    if not github_cli.logged_in():
        print("You are not logged in with GitHub CLI. Follow instructions below.")
        github_cli.log_in()

    if not radix_cli.logged_in():
        print("You are not logged in with Radix CLI. Follow instructions below.")
        radix_cli.log_in()

    repository_url = f"https://github.com/{github_slug}"
    if github_cli.repo_exists(github_slug):
        raise ValueError(f"GitHub repository {github_slug} already exists.")

    radix_config = radix_configuration()

    azure_configuration_values = azure_configuration()

    interactive_terminal.terminal_title("Initializing automatic deployment")

    progress_bar = tqdm.tqdm(total=15, bar_format="{l_bar} {bar} |")

    progress_bar.write("✓ Configuring Azure app registration")
    azure_configuration_values.update(
        azure_cli.azure_app_registration_setup(
            display_name=azure_configuration_values["display_name"],
            proxy_redirect_url=radix_config["app_url"] + "/oauth2/callback",
        )
    )
    progress_bar.update()

    # Give Azure some seconds to store the enterprise application
    # before opening the link for the user:
    time.sleep(5)
    webbrowser.open(
        "https://portal.azure.com/#blade/Microsoft_AAD_IAM/ManagedAppMenuBlade/Users/"
        f"objectId/{azure_configuration_values['object_id']}/"
        f"appId/{azure_configuration_values['app_registration_id']}"
    )

    progress_bar.write("✓ Uploading Webviz file resources to Azure storage container.")
    azure_cli.storage_container_upload_folder(
        subscription=azure_configuration_values["subscription"],
        resource_group=azure_configuration_values["resource_group"],
        storage_name=azure_configuration_values["storage_account_name"],
        container_name=azure_configuration_values["storage_container_name"],
        source_folder=build_directory / "resources",
    )
    progress_bar.update()

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir = pathlib.Path(tmp_dir)

        progress_bar.write(f"✓ Creating new private repository ({repository_url})")
        cloned_path = github_cli.create_github_repository(
            github_slug, directory=temp_dir
        )
        progress_bar.update()

        progress_bar.write("✓ Adding files to GitHub repository.")
        dict_to_store = {
            "azure": {
                key: value
                for key, value in azure_configuration_values.items()
                if "secret" not in key
            },
            "radix": radix_config,
        }
        (build_directory / "deploy_settings.json").write_text(
            json.dumps(dict_to_store, indent=4, sort_keys=True)
        )
        create_radix_config(
            build_directory,
            {
                "app_registration_id": azure_configuration_values[
                    "app_registration_id"
                ],
                "application_name": radix_config["application_name"],
                "azure_storage_container_name": azure_configuration_values[
                    "storage_container_name"
                ],
                "tenant_id": azure_configuration_values["tenant_id"],
            },
        )
        github_cli.commit_portable_webviz(
            github_slug=github_slug, source_directory=build_directory
        )
        (build_directory / "deploy_settings.json").unlink()
        (build_directory / "radixconfig.yaml").unlink()
        progress_bar.update()

        progress_bar.write(
            "✓ Turning on GitHub repository dependency vulnerability alerts."
        )
        github_cli.turn_on_github_vulnerability_alers(directory=cloned_path)
        progress_bar.update()

        progress_bar.write(
            f"✓ Creating Radix application '{radix_config['application_name']}' "
            f"in {radix_config['context']}."
        )
        webhook_secret = secrets.token_urlsafe()
        public_key = radix_cli.create_application(
            application_name=radix_config["application_name"],
            owner_email=radix_config["owner_email"],
            repository_url=repository_url,
            shared_secret=webhook_secret,
            wbs=radix_config["wbs"],
            context=radix_config["context"],
        )
        progress_bar.update()

        # Wait for application to be reconciled
        time.sleep(5)

        progress_bar.write(
            "✓ Adding webhook from GitHub repository to Radix application."
        )
        github_cli.add_webhook(
            directory=cloned_path,
            receiver_url=radix_config["webhook_receiver_url"],
            secret=webhook_secret,
        )
        progress_bar.update()

        progress_bar.write("✓ Adding Radix deploy key to GitHub repository.")
        github_cli.add_deploy_key(
            directory=cloned_path, title="Radix deploy key", key=public_key
        )
        progress_bar.update()

    # Wait for application to be reconciled
    time.sleep(5)

    progress_bar.write("✓ Initializing build workflow of Radix application.")
    radix_cli.build_and_deploy_application(
        application_name=radix_config["application_name"],
        context=radix_config["context"],
    )
    progress_bar.update()

    progress_bar.write(
        "✓ Setting Radix secrets when Radix has built the application... "
        "please wait (approx. 3-4 min)."
    )
    for key, value in {
        "OAUTH2_PROXY_CLIENT_SECRET": azure_configuration_values["proxy_client_secret"],
        "OAUTH2_PROXY_COOKIE_SECRET": azure_configuration_values["proxy_cookie_secret"],
        "OAUTH2_PROXY_REDIRECT_URL": azure_configuration_values["proxy_redirect_url"],
    }.items():
        radix_cli.set_radix_secret(
            application_name=radix_config["application_name"],
            environment="prod",
            component="auth",
            key=key,
            value=value,
            context=radix_config["context"],
        )
        progress_bar.write(f"  ✓ Radix '{key}' secret set.")
        progress_bar.update()

    for key, value in {
        "main-appstorage-csiazurecreds-accountkey": azure_configuration_values[
            "storage_account_key_secret"
        ],
        "main-appstorage-csiazurecreds-accountname": azure_configuration_values[
            "storage_account_name"
        ],
    }.items():
        radix_cli.set_radix_secret(
            application_name=radix_config["application_name"],
            environment="prod",
            component="main",
            key=key,
            value=value,
            context=radix_config["context"],
        )
        progress_bar.write(f"  ✓ Radix '{key}' secret set.")
        progress_bar.update()

    progress_bar.write("✓ Waiting on Radix application to start and become online.")
    while not website_online(radix_config["app_url"]):
        time.sleep(10)

    progress_bar.update()
    progress_bar.write(
        "✓ Application successfully deployed and online at " + radix_config["app_url"]
    )

    progress_bar.close()

    webbrowser.open(radix_config["app_url"])


def radix_redeploy(github_slug: str, build_directory: pathlib.Path) -> None:

    deploy_settings = json.loads(
        github_cli.read_file_in_repository(github_slug, "deploy_settings.json")
    )
    github_cli.commit_portable_webviz(
        github_slug, build_directory, commit_message="Update"
    )

    azure_cli.storage_container_upload_folder(
        subscription=deploy_settings["azure"]["subscription"],
        resource_group=deploy_settings["azure"]["resource_group"],
        storage_name=deploy_settings["azure"]["storage_account_name"],
        container_name=deploy_settings["azure"]["storage_container_name"],
        source_folder=build_directory / "resources",
    )


def main_radix_deployment(args: argparse.Namespace) -> None:

    if sys.version_info < (3, 8):
        raise RuntimeError("Radix deployment workflow requires at least Python 3.8")

    if not args.portable_app.is_dir():
        raise ValueError(f"{args.portable_app} is not a directory.")

    if args.initial_deploy:
        radix_initial_deployment(args.github_slug, args.portable_app)
    else:
        radix_redeploy(args.github_slug, args.portable_app)
