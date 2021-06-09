# pylint: disable=invalid-sequence-index

import logging
import os
import time
import secrets
import pathlib
import warnings
import webbrowser
import contextlib
import subprocess
from typing import List, Dict, Optional, Tuple, Any

try:
    import azure.cli.core
    from azure.common import AzureHttpError
    from azure.core.exceptions import HttpResponseError
    from msrestazure.azure_exceptions import CloudError

    AZURE_CLI_INSTALLED = True
except ModuleNotFoundError:
    AZURE_CLI_INSTALLED = False

PIMCOMMON_URL = (
    "https://portal.azure.com/#blade/Microsoft_Azure_PIMCommon/ActivationMenuBlade"
)


def _azure_cli(args: List[str], devnull_stderr: bool = True) -> Any:
    """Runs an Azure CLI command using the Azure Python library."""

    # When returning errors, azure cli seems to close the stderr stream similar to
    # https://github.com/pytest-dev/pytest/issues/5502
    # This makes it impossible to catch an error and later perform a new call
    # to azure cli.
    # Therefore cleaning the root logger as suggested in
    # https://github.com/pytest-dev/pytest/issues/5502#issuecomment-647157873
    loggers = [logging.getLogger()] + list(
        logging.Logger.manager.loggerDict.values()  # type: ignore[attr-defined, arg-type]
    )
    for logger in loggers:
        handlers = getattr(logger, "handlers", [])
        for handler in handlers:
            logger.removeHandler(handler)

    cli = azure.cli.core.get_default_cli()
    with open(os.devnull, "w") as out_file:
        # contextlib.nullcontext available only in Python 3.7+
        if devnull_stderr:
            with contextlib.redirect_stderr(out_file):
                cli.invoke(args, out_file=out_file)
        else:
            cli.invoke(args, out_file=out_file)

    if cli.result.error:
        raise cli.result.error

    return cli.result.result


def logged_in() -> bool:
    """Returns true if user is logged into Azure,
    otherwise returns False.
    """
    # No easy way currently checking if logged in.
    # https://github.com/Azure/azure-cli/issues/6802

    if not AZURE_CLI_INSTALLED:
        raise RuntimeError(
            "In order to use webviz deploy features, you need to first install "
            "the optional deploy dependencies. You can do this by e.g. running "
            "'pip install webviz-config[deployment]'"
        )

    try:
        _azure_cli(["account", "list-locations"], devnull_stderr=False)
        return True
    except azure.cli.core.CLIError:
        return False


def log_in() -> None:
    _azure_cli(["login", "--use-device-code"])


def subscriptions() -> List[str]:
    """Returns list of all Azure subscriptions logged in user has read access to."""
    return [group["name"] for group in _azure_cli(["account", "list"])]


def resource_groups(subscription: str) -> List[str]:
    """Returns list of all Azure resource group names logged in user has read access to
    within given subscription."""
    try:
        return [
            group["name"]
            for group in _azure_cli(["group", "list", "--subscription", subscription])
        ]
    except CloudError:  # AuthorizationFailed
        return []


def storage_account_name_available(name: str) -> Tuple[bool, str]:
    result = _azure_cli(["storage", "account", "check-name", "--name", name])
    return (result["nameAvailable"], result["message"])


def storage_account_exists(name: str, subscription: str, resource_group: str) -> bool:
    accounts = _azure_cli(
        ["storage", "account", "list", "--subscription", subscription]
    )

    for account in accounts:
        if account["name"] == name:
            if account["resourceGroup"] != resource_group:
                warnings.warn(
                    f"Storage account with name {name} found, but it belongs "
                    f"to another resource group ({account['resourceGroup']}."
                )
            return True

    return False


def storage_container_exists(
    container_name: str, account_name: str, subscription: str
) -> bool:
    containers = _azure_cli(
        [
            "storage",
            "container",
            "list",
            "--account-name",
            account_name,
            "--auth-mode",
            "login",
            "--subscription",
            subscription,
        ]
    )
    return any(container["name"] == container_name for container in containers)


def create_storage_account(subscription: str, resource_group: str, name: str) -> None:
    """Creates an Azure storage account. Also adds upload access, as well
    as possibility to list/generate access keys, to the user creating it
    (i.e. the currently logged in user).

    Note that Azure documentation states that it can take up to five minutes
    after the command has finished until the added access is enabled in practice.
    """

    azure_pim_already_open = False

    while True:
        try:
            _azure_cli(
                [
                    "storage",
                    "account",
                    "create",
                    "--subscription",
                    subscription,
                    "--resource-group",
                    resource_group,
                    "--name",
                    name,
                    "--location",
                    "northeurope",
                    "--sku",
                    "Standard_ZRS",
                    "--encryption-services",
                    "blob",
                ]
            )
            break
        except (HttpResponseError, CloudError) as exc:
            if "AuthorizationFailed" in str(exc):
                if not azure_pim_already_open:
                    webbrowser.open(f"{PIMCOMMON_URL}/azurerbac")
                    print(
                        "Not able to create new storage account. Do you have "
                        "enough priviliges to do it? We automatically opened the URL "
                        "to where you activate Azure PIM. Please activate necessary "
                        "priviliges. You need to be 'Owner' of the subscription in "
                        "order to both create the new account and assign user "
                        "roles to it afterwards."
                    )
                    azure_pim_already_open = True
                print("New attempt of app registration in 1 minute.")
                time.sleep(60)
            else:
                raise RuntimeError("Not able to create new storage account.") from exc

    user_id: str = _azure_cli(
        ["ad", "signed-in-user", "show", "--query", "objectId", "-o", "tsv"]
    )
    resource_group_id: str = _azure_cli(
        ["group", "show", "--subscription", subscription, "--name", resource_group]
    )["id"]

    for role in [
        "Storage Blob Data Contributor",
        "Storage Account Key Operator Service Role",
    ]:
        _azure_cli(
            [
                "role",
                "assignment",
                "create",
                "--role",
                role,
                "--assignee",
                user_id,
                "--scope",
                f"{resource_group_id}/providers/Microsoft.Storage/storageAccounts/{name}",
            ]
        )


def get_storage_account_access_key(subscription: str, account_name: str) -> str:
    result = _azure_cli(
        [
            "storage",
            "account",
            "keys",
            "list",
            "--account-name",
            account_name,
            "--subscription",
            subscription,
        ]
    )

    return result[0]["value"]


def create_storage_container(
    subscription: str, storage_account: str, container: str
) -> None:
    """Creates a container in given storage account."""
    _azure_cli(
        [
            "storage",
            "container",
            "create",
            "--account-name",
            storage_account,
            "--name",
            container,
            "--auth-mode",
            "login",
            "--subscription",
            subscription,
        ]
    )


def storage_container_upload_folder(
    storage_name: str,
    container_name: str,
    destination_folder: str,
    source_folder: pathlib.Path,
) -> None:
    # If the upload access was recently added, Azure documentation
    # says it can take up until five minutes before the access is
    # enabled in practice.

    command_arguments = [
        "storage",
        "blob",
        "upload-batch",
        "--account-name",
        storage_name,
        "--destination",
        f"{container_name}/{destination_folder}",
        "--auth-mode",
        "login",
        "--source",
        str(source_folder),
    ]

    for _ in range(5):
        try:
            _azure_cli(
                command_arguments,
                devnull_stderr=False,  # progress status shown in stderr by Azure CLI...
            )
            return
        except AzureHttpError:
            pass
        except ValueError:
            print(
                "====================================================================\n"
                "Ignore the 'ValueError: I/O operation on closed file' above.\n"
                "There is currently a bug in the Azure Python CLI that hits when you\n"
                " 1) Create a new Azure storage account.\n"
                " 2) Upload to the new storage account in the same Python session.\n\n"
                "We will try to upload in a subprocess.\n"
                "===================================================================="
            )

            result = subprocess.run(  # pylint: disable=subprocess-run-check
                ["az"] + command_arguments,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # capture_output=True, <-- First vailable in Python 3.7
            )

            if not b"ERROR" in result.stderr:
                # Azure CLI shows progress in stderr,
                # i.e. even successfull runs have content in stderr
                return
        finally:
            print("Waiting on Azure access activation... please wait.")
            time.sleep(60)

    raise RuntimeError("Not able to upload folder to blob storage container.")


def appservice_plan_list() -> List[str]:
    """Returns list of all Azure resource group names logged in user has access to."""
    return [group["name"] for group in _azure_cli(["appservice", "plan", "list"])]


def existing_app_registration(display_name: str) -> Optional[str]:
    existing = _azure_cli(["ad", "app", "list", "--display-name", display_name])
    if existing:
        return existing[0]["appId"]
    return None


def create_app_registration(display_name: str) -> str:

    existing = existing_app_registration(display_name)

    return (
        existing
        if existing is not None
        else _azure_cli(
            [
                "ad",
                "app",
                "create",
                "--display-name",
                display_name,
            ]
        )["appId"]
    )


def create_secret(
    app_registration_id: str, secret_description: str, years: int = 100
) -> str:
    new_secret = secrets.token_urlsafe()
    _azure_cli(
        [
            "ad",
            "app",
            "credential",
            "reset",
            "--append",
            "--id",
            app_registration_id,
            "--credential-description",
            secret_description,
            "--password",
            new_secret,
            "--years",
            str(years),
        ]
    )
    return new_secret


def add_reply_url(app_registration_id: str, reply_url: str) -> None:
    """Will add web reply url to given app registration id, if it does not alredy exist."""

    app_data = _azure_cli(["ad", "app", "show", "--id", app_registration_id])

    reply_urls = app_data["replyUrls"]
    if reply_url not in reply_urls:
        reply_urls.append(reply_url)

    _azure_cli(
        [
            "ad",
            "app",
            "update",
            "--id",
            app_registration_id,
            "--reply-urls",
        ]
        + reply_urls
    )


def create_service_principal(app_registration_id: str) -> Tuple[str, str]:
    existing_service_principal = _azure_cli(
        ["ad", "sp", "list", "--filter", f"appId eq '{app_registration_id}'"]
    )

    service_principal = (
        existing_service_principal[0]
        if existing_service_principal
        else _azure_cli(["ad", "sp", "create", "--id", app_registration_id])
    )

    object_id = service_principal["objectId"]

    _azure_cli(
        [
            "ad",
            "sp",
            "update",
            "--id",
            object_id,
            "--set",
            "appRoleAssignmentRequired=true",
        ]
    )

    return object_id, service_principal["appOwnerTenantId"]


def azure_app_registration_setup(
    display_name: str, proxy_redirect_url: str
) -> Dict[str, str]:

    azure_pim_already_open = False

    while True:
        try:
            app_registration_id = create_app_registration(display_name)
            object_id, tenant_id = create_service_principal(app_registration_id)
            break
        except azure.cli.core.CLIError as exc:

            if not azure_pim_already_open:
                webbrowser.open(f"{PIMCOMMON_URL}/aadmigratedroles")
                azure_pim_already_open = True

                print(exc)
                print(
                    "Not able to create new app registration. Do you have enough priviliges "
                    "to do it? We automatically opened the URL to where you activate Azure PIM. "
                    "Please active necessary priviliges."
                )

            print("New attempt of app registration in 1 minute.")
            time.sleep(60)

    proxy_client_secret = create_secret(app_registration_id, "cli secret")
    add_reply_url(app_registration_id, proxy_redirect_url)

    return {
        "app_registration_id": app_registration_id,
        "object_id": object_id,
        "proxy_client_secret": proxy_client_secret,
        "proxy_cookie_secret": secrets.token_urlsafe(nbytes=16),
        "proxy_redirect_url": proxy_redirect_url,
        "tenant_id": tenant_id,
    }
