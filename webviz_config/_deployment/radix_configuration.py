import functools
from typing import Dict

from . import interactive_terminal
from . import radix_cli


def radix_configuration() -> Dict[str, str]:

    interactive_terminal.terminal_title("Radix cluster")
    radix_context = interactive_terminal.user_input_from_list(
        "WEBVIZ_RADIX_CONTEXT", "Radix context", ["production", "playground"]
    )
    radix_subdomain = "radix.equinor.com"
    if radix_context == "playground":
        radix_subdomain = "playground." + radix_subdomain

    interactive_terminal.terminal_title("Radix application name")
    radix_application_name = interactive_terminal.user_input_optional_reuse(
        "WEBVIZ_RADIX_APPLICATION",
        "Radix application",
        functools.partial(radix_cli.application_exists, context=radix_context),
        reuse_allowed=False,
    )

    interactive_terminal.terminal_title("Radix owner e-mail")
    radix_owner_email = interactive_terminal.user_input_from_stdin(
        "WEBVIZ_RADIX_EMAIL", "e-mail", regex=r"[^@]+@[^@]+\.[^@]+"
    )

    interactive_terminal.terminal_title(
        "WBS to use for Radix application cost allocation"
    )
    radix_wbs = interactive_terminal.user_input_from_stdin(
        "WEBVIZ_RADIX_WBS", "WBS", regex=r"[a-zA-Z0-9]+\.+[a-zA-Z0-9.]*[a-zA-Z0-9]"
    )

    return {
        "context": radix_context,
        "application_name": radix_application_name,
        "owner_email": radix_owner_email,
        "wbs": radix_wbs,
        "app_url": f"https://{radix_application_name}.app.{radix_subdomain}",
        "webhook_receiver_url": f"https://webhook.{radix_subdomain}/events/github",
    }
