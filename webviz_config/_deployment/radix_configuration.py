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

    return {
        "context": radix_context,
        "application_name": radix_application_name,
        "app_url": f"https://{radix_application_name}.app.{radix_subdomain}",
        "webhook_receiver_url": f"https://webhook.{radix_subdomain}/events/github",
    }
