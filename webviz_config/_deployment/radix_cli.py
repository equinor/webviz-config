import time
import shutil
import pathlib
import subprocess


def binary_available() -> bool:
    """Returns True if the Radix CLI binary (rx) is
    availabile in $PATH, otherwise returns False.
    """
    return shutil.which("rx") is not None


def _trigger_token_aquisition(update_only: bool = False) -> None:
    # There exist no pure login command in rx as of April 2021
    # See https://github.com/equinor/radix-cli/issues/20.
    # pylint: disable=subprocess-run-check
    subprocess.run(
        [
            "rx",
            "get",
            "application",
            "--application",
            "dummy_name",
            "--context",
            "dummy_context",
        ],
        timeout=15 if update_only else None,
        capture_output=update_only,
    )


def logged_in() -> bool:

    _trigger_token_aquisition(update_only=True)

    config = pathlib.Path.home() / ".radix" / "config"
    return config.is_file()


def log_in() -> None:
    _trigger_token_aquisition()


def application_exists(application_name: str, context: str) -> bool:
    result = subprocess.run(
        [
            "rx",
            "get",
            "application",
            "--application",
            application_name,
            "--context",
            context,
        ],
        capture_output=True,
        check=False,
    )
    return not result.stderr


def create_application(
    application_name: str,
    configuration_item: str,
    repository_url: str,
    shared_secret: str,
    context: str,
    ad_group: str,
) -> str:
    result = subprocess.run(
        [
            "rx",
            "create",
            "application",
            "--application",
            application_name,
            "--config-branch",
            "main",
            "--configuration-item",
            configuration_item,
            "--repository",
            repository_url,
            "--shared-secret",
            shared_secret,
            "--context",
            context,
            "--ad-groups",
            ad_group,
        ],
        capture_output=True,
        check=True,
    )

    stderr = result.stderr.decode()
    if not stderr.startswith("ssh-rsa"):
        pass  # https://github.com/equinor/radix-cli/issues/48
        # error_message = stderr
        # if "registerApplicationBadRequest" in stderr:
        #     error_message += (
        #         f"Is {repository_url} being used by another Radix application?"
        #     )
        # raise RuntimeError(error_message)

    return stderr


def build_and_deploy_application(application_name: str, context: str) -> None:
    subprocess.run(
        [
            "rx",
            "create",
            "job",
            "build-deploy",
            "--application",
            application_name,
            "--branch",
            "main",
            "--context",
            context,
        ],
        check=True,
    )


def set_radix_secret(
    application_name: str,
    environment: str,
    component: str,
    key: str,
    value: str,
    context: str,
) -> None:

    max_radix_build_time = 60 * 60
    sleep_per_attempt = 10

    for _ in range(max_radix_build_time // sleep_per_attempt):
        try:
            subprocess.run(
                [
                    "rx",
                    "set",
                    "environment-secret",
                    "--await-reconcile",
                    "--application",
                    application_name,
                    "--environment",
                    environment,
                    "--component",
                    component,
                    "--secret",
                    key,
                    "--value",
                    value,
                    "--context",
                    context,
                ],
                capture_output=True,
                check=True,
            )
            return
        except subprocess.CalledProcessError:
            time.sleep(sleep_per_attempt)

    raise RuntimeError("Failed setting Radix secret. Is Radix still building?")
