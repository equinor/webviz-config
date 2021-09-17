import functools
from typing import Dict

from . import interactive_terminal
from . import azure_cli


def azure_configuration() -> Dict[str, str]:
    # Select Azure subscription
    interactive_terminal.terminal_title("Azure subscription")
    subscription = interactive_terminal.user_input_from_list(
        env_var="WEBVIZ_AZURE_SUBSCRIPTION",
        noun="subscription",
        choices=azure_cli.subscriptions(),
    )

    # Select resource group
    interactive_terminal.terminal_title("Azure resource group")
    resource_group = interactive_terminal.user_input_from_list(
        env_var="WEBVIZ_AZURE_RESOURCE_GROUP",
        noun="resource group",
        choices=azure_cli.resource_groups(subscription),
    )

    # Choose app registration
    interactive_terminal.terminal_title("Azure app registration")
    display_name = interactive_terminal.user_input_optional_reuse(
        env_var="WEBVIZ_AZURE_APP_REGISTRATION_DISPLAY_NAME",
        noun="app registration",
        exists_function=azure_cli.existing_app_registration,
    )

    # Choose Azure storage account
    storage_account_exists = functools.partial(
        azure_cli.storage_account_exists,
        subscription=subscription,
        resource_group=resource_group,
    )

    interactive_terminal.terminal_title("Azure storage account")
    storage_account_name = interactive_terminal.user_input_optional_reuse(
        env_var="WEBVIZ_AZURE_STORAGE_ACCOUNT",
        noun="storage account",
        exists_function=storage_account_exists,
        regex="^[a-z0-9]{3,24}$",
    )

    if not storage_account_exists(storage_account_name):
        azure_cli.create_storage_account(
            subscription, resource_group, storage_account_name
        )
        print("✓ Created storage account.")

    # Choose Azure storage container
    storage_container_exists = functools.partial(
        azure_cli.storage_container_exists,
        account_name=storage_account_name,
        subscription=subscription,
        resource_group=resource_group,
    )

    interactive_terminal.terminal_title("Azure storage container")

    storage_container_name = interactive_terminal.user_input_optional_reuse(
        env_var="WEBVIZ_AZURE_STORAGE_CONTAINER",
        noun="storage container",
        exists_function=storage_container_exists,
    )

    if not storage_container_exists(storage_container_name):
        azure_cli.create_storage_container(
            subscription=subscription,
            resource_group=resource_group,
            storage_account=storage_account_name,
            container=storage_container_name,
        )
        print(f"✓ Created storage container '{storage_container_name}'.")

    return {
        "subscription": subscription,
        "resource_group": resource_group,
        "storage_account_name": storage_account_name,
        "storage_account_key_secret": azure_cli.get_storage_account_access_key(
            subscription=subscription,
            resource_group=resource_group,
            account_name=storage_account_name,
        ),
        "storage_container_name": storage_container_name,
        "display_name": display_name,
    }
