import time
import functools
import secrets
import asyncio
import pathlib
import datetime
import warnings
import webbrowser
from typing import List, Dict, Optional, Tuple

import requests
from tqdm.asyncio import tqdm

try:
    from azure.identity import InteractiveBrowserCredential
    from azure.core.exceptions import HttpResponseError
    from azure.mgmt.resource.subscriptions import SubscriptionClient
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.storage.blob import BlobServiceClient
    from azure.storage.blob.aio import ContainerClient

    AZURE_CLI_INSTALLED = True
except ModuleNotFoundError:
    AZURE_CLI_INSTALLED = False

GRAPH_BASE_URL = "https://graph.microsoft.com"
PIMCOMMON_URL = (
    "https://portal.azure.com/#blade/Microsoft_Azure_PIMCommon/ActivationMenuBlade"
)


@functools.lru_cache
def _credential():  # type: ignore[no-untyped-def]
    if not AZURE_CLI_INSTALLED:
        raise RuntimeError(
            "In order to use webviz deploy features, you need to first install "
            "the optional deploy dependencies. You can do this by e.g. running "
            "'pip install webviz-config[deployment]'"
        )

    return InteractiveBrowserCredential()


def _subscription_id(subscription_name: str = None) -> str:
    subscription_list = SubscriptionClient(_credential()).subscriptions.list()

    if subscription_name is None:
        return next(subscription_list).subscription_id

    for sub in subscription_list:
        if sub.display_name == subscription_name:
            return sub.subscription_id

    raise ValueError(f"Could not find a subscription with name {subscription_name}")


def _connection_string(
    subscription: str, resource_group: str, storage_account: str
) -> str:
    key = get_storage_account_access_key(subscription, resource_group, storage_account)
    return (
        f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={key}"
    )


def subscriptions() -> List[str]:
    """Returns list of all Azure subscriptions logged in user has read access to."""
    return [
        sub.display_name
        for sub in SubscriptionClient(_credential()).subscriptions.list()
    ]


def resource_groups(subscription: str) -> List[str]:
    """Returns list of all Azure resource group names logged in user has read access to
    within given subscription."""

    rmc = ResourceManagementClient(_credential(), _subscription_id(subscription))
    return [rg.name for rg in rmc.resource_groups.list()]


def storage_account_name_available(name: str) -> Tuple[bool, str]:
    storage_client = StorageManagementClient(_credential(), _subscription_id())
    result = storage_client.storage_accounts.check_name_availability({"name": name})
    return (result.name_available, result.message)


def storage_account_exists(name: str, subscription: str, resource_group: str) -> bool:
    storage_client = StorageManagementClient(
        _credential(), _subscription_id(subscription)
    )

    if any(
        account.name == name
        for account in storage_client.storage_accounts.list_by_resource_group(
            resource_group
        )
    ):
        return True

    for account in storage_client.storage_accounts.list():
        if account.name == name:
            if account.resourceGroup != resource_group:
                warnings.warn(
                    f"Storage account with name {name} found, but it belongs "
                    f"to another resource group ({account.resourceGroup}."
                )
            return True

    return False


def storage_container_exists(
    container_name: str, account_name: str, subscription: str, resource_group: str
) -> bool:
    storage_client = StorageManagementClient(
        _credential(), _subscription_id(subscription)
    )
    containers = storage_client.blob_containers.list(resource_group, account_name)
    return any(container.name == container_name for container in containers)


def create_storage_account(subscription: str, resource_group: str, name: str) -> None:
    """Creates an Azure storage account. Also adds upload access, as well
    as possibility to list/generate access keys, to the user creating it
    (i.e. the currently logged in user).

    Note that Azure documentation states that it can take up to five minutes
    after the command has finished until the added access is enabled in practice.
    """

    storage_client = StorageManagementClient(
        _credential(), _subscription_id(subscription)
    )

    azure_pim_already_open = False

    while True:
        try:
            return storage_client.storage_accounts.begin_create(
                resource_group,
                name,
                {
                    "sku": {"name": "Standard_ZRS"},
                    "kind": "StorageV2",
                    "location": "northeurope",
                    "encryption": {
                        "key_source": "Microsoft.Storage",
                        "services": {"blob": {"key_type": "Account", "enabled": True}},
                    },
                },
            ).result()
        except HttpResponseError as exc:
            if "AuthorizationFailed" in str(exc):
                if not azure_pim_already_open:
                    webbrowser.open(f"{PIMCOMMON_URL}/azurerbac")
                    print(
                        "Not able to create new storage account. Do you have "
                        "enough priviliges to do it? We automatically opened the URL "
                        "to where you activate Azure PIM. Please activate/add necessary "
                        "priviliges."
                    )
                    azure_pim_already_open = True
                print("New attempt of creating storage account in 30 seconds.")
                time.sleep(30)
            else:
                raise RuntimeError("Not able to create new storage account.") from exc


def get_storage_account_access_key(
    subscription: str,
    resource_group: str,
    account_name: str,
) -> str:
    storage_client = StorageManagementClient(
        _credential(), _subscription_id(subscription)
    )

    azure_pim_already_open = False

    while True:
        try:
            return (
                storage_client.storage_accounts.list_keys(resource_group, account_name)
                .keys[0]
                .value
            )
        except HttpResponseError as exc:
            if "AuthorizationFailed" in str(exc):
                if not azure_pim_already_open:
                    webbrowser.open(f"{PIMCOMMON_URL}/azurerbac")
                    print(
                        "Not able to get access keys for storage account. Do you have "
                        "enough priviliges to do it? We automatically opened the URL "
                        "to where you activate Azure PIM. Please activate/add necessary "
                        "priviliges. If not inherited from higher privileges, you will "
                        "as a minmium need role 'Storage Account Key Operator Service Role' "
                        f"for the storage account {account_name}."
                    )
                    azure_pim_already_open = True
                print("New attempt of getting storage account keys in 30 seconds.")
                time.sleep(30)
            else:
                raise RuntimeError("Not able to get storage account keys.") from exc


def create_storage_container(
    subscription: str,
    resource_group: str,
    storage_account: str,
    container: str,
) -> None:
    BlobServiceClient.from_connection_string(  # type: ignore[attr-defined]
        _connection_string(subscription, resource_group, storage_account)
    ).get_container_client(container).create_container()


def storage_container_upload_folder(
    subscription: str,
    resource_group: str,
    storage_name: str,
    container_name: str,
    source_folder: pathlib.Path,
) -> None:

    paths_to_upload = [path for path in source_folder.rglob("*") if path.is_file()]

    async def _upload_file(
        container_client: ContainerClient,
        path: pathlib.Path,
        source_folder: pathlib.Path,
        semaphore: asyncio.Semaphore,
    ) -> None:
        async with semaphore:
            with open(path, "rb") as file_handle:
                await container_client.upload_blob(
                    name=path.relative_to(source_folder).as_posix(),
                    data=file_handle,
                    overwrite=True,
                )

    async def _upload_blob() -> None:
        async with ContainerClient.from_connection_string(  # type: ignore[attr-defined]
            _connection_string(subscription, resource_group, storage_name),
            container_name,
        ) as container_client:

            class UploadTasks:
                def __init__(
                    self, paths_to_upload: List[pathlib.Path], max_open_files: int = 100
                ):
                    self.index = 0
                    self.paths_to_upload = paths_to_upload
                    self.semaphore = asyncio.Semaphore(max_open_files)

                # Forward reference not possible on Python 3.6:
                def __iter__(self):  # type: ignore[no-untyped-def]
                    return self

                def __next__(self) -> asyncio.Task:
                    try:
                        task = asyncio.create_task(
                            _upload_file(
                                container_client,
                                self.paths_to_upload[self.index],
                                source_folder,
                                self.semaphore,
                            )
                        )
                    except IndexError as exc:
                        raise StopIteration from exc
                    self.index += 1
                    return task

                def __len__(self) -> int:
                    return len(self.paths_to_upload)

            for task in tqdm.as_completed(
                UploadTasks(paths_to_upload),
                bar_format="{l_bar} {bar} | Uploaded {n_fmt}/{total_fmt}",
            ):
                await task

    asyncio.run(_upload_blob())


def _graph_headers() -> Dict[str, str]:
    token = _credential().get_token(f"{GRAPH_BASE_URL}/.default").token
    return {"Authorization": f"bearer {token}", "Content-type": "application/json"}


def _object_id_from_app_id(app_registration_id: str) -> str:
    endpoint = f"applications?$filter=appID eq '{app_registration_id}'"

    data = requests.get(
        f"{GRAPH_BASE_URL}/v1.0/{endpoint}",
        headers=_graph_headers(),
    ).json()

    object_id = data["value"][0]["id"]
    return object_id


def existing_app_registration(display_name: str) -> Optional[str]:
    """Returns application (client) ID with given display_name if it exists,
    otherwise returns None.
    """
    endpoint = f"applications?$filter=displayName eq '{display_name}'"
    data = requests.get(
        f"{GRAPH_BASE_URL}/v1.0/{endpoint}", headers=_graph_headers()
    ).json()

    if data["value"]:
        return data["value"][0]["appId"]
    return None


def create_app_registration(display_name: str) -> str:

    existing_app_id = existing_app_registration(display_name)
    if existing_app_id is not None:
        return existing_app_id

    data = requests.post(
        f"{GRAPH_BASE_URL}/v1.0/applications",
        json={"displayName": display_name, "signInAudience": "AzureADMyOrg"},
        headers=_graph_headers(),
    ).json()

    if "error" in data and data["error"]["code"] == "Authorization_RequestDenied":
        raise PermissionError("Insufficient privileges to create new app registration.")

    app_id = data["appId"]

    webbrowser.open(
        "https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/"
        f"ApplicationMenuBlade/Manifest/appId/{app_id}"
    )

    input(
        """
    Due to current limitations in Microsoft Graph API
    (https://docs.microsoft.com/en-us/azure/active-directory/develop/reference-app-manifest),
    we need to update the app manifest manually. In the browser tab that was opened,
    please update "oauth2Permissions" to this:

    	"oauth2Permissions": [
		{
			"adminConsentDescription": "Access on behalf of the signed-in user",
			"adminConsentDisplayName": "Access on behalf of the signed-in user",
			"id": "00000000-0000-0000-0000-000000000001",
			"isEnabled": true,
			"lang": null,
			"origin": "Application",
			"type": "User",
			"userConsentDescription": "Access application on your behalf",
			"userConsentDisplayName": "Access application on your behalf",
			"value": "user_impersonation"
		}
	],

    Press enter to continue."""
    )

    return app_id


def create_secret(app_registration_id: str, secret_description: str) -> str:

    object_id = _object_id_from_app_id(app_registration_id)

    end_datetime = datetime.datetime.now() + datetime.timedelta(days=365)
    data = requests.post(
        f"{GRAPH_BASE_URL}/v1.0/applications/{object_id}/addPassword",
        json={
            "passwordCredential": {
                "displayName": secret_description,
                "endDateTime": end_datetime.isoformat(),
            }
        },
        headers=_graph_headers(),
    ).json()

    return data["secretText"]


def add_reply_url(app_registration_id: str, reply_url: str) -> None:
    """Will add web reply url to given app registration id, if it does not alredy exist."""

    object_id = _object_id_from_app_id(app_registration_id)

    data = requests.get(
        f"{GRAPH_BASE_URL}/v1.0/applications/{object_id}",
        headers=_graph_headers(),
    ).json()

    web = data["web"]

    if reply_url not in web["redirectUris"]:
        web["redirectUris"].append(reply_url)

    requests.patch(
        f"{GRAPH_BASE_URL}/v1.0/applications/{object_id}",
        json={"web": web},
        headers=_graph_headers(),
    )


def create_service_principal(app_registration_id: str) -> Tuple[str, str]:

    endpoint = f"servicePrincipals?$filter=appID eq '{app_registration_id}'"
    data = requests.get(
        f"{GRAPH_BASE_URL}/v1.0/{endpoint}",
        headers=_graph_headers(),
    ).json()

    if "error" not in data and data["value"]:
        data_object = data["value"][0]
        if not data_object["appRoleAssignmentRequired"]:
            raise RuntimeError(
                "Service principal already exists, and it does not require app role "
                "assignments. Deployment stopped, as this should be set to true in "
                "order to secure access."
            )
    else:
        data_object = requests.post(
            f"{GRAPH_BASE_URL}/v1.0/servicePrincipals",
            json={"appId": app_registration_id, "appRoleAssignmentRequired": True},
            headers=_graph_headers(),
        ).json()

        if "error" in data:
            raise RuntimeError(f"Graph query failed with response {data}")

    object_id = data_object["id"]
    directory_tenant_id = data_object["appOwnerOrganizationId"]

    return object_id, directory_tenant_id


def azure_app_registration_setup(
    display_name: str, proxy_redirect_url: str
) -> Dict[str, str]:

    azure_pim_already_open = False

    while True:
        try:
            app_registration_id = create_app_registration(display_name)
            object_id, tenant_id = create_service_principal(app_registration_id)
            break
        except PermissionError:
            if not azure_pim_already_open:
                webbrowser.open(f"{PIMCOMMON_URL}/aadmigratedroles")
                azure_pim_already_open = True

                print(
                    "Not able to create new app registration. Do you have enough "
                    "priviliges to do it? We automatically opened the URL where you "
                    "can activate Azure PIM. Please activate necessary priviliges."
                )

            print("New attempt of app registration in 30 seconds.")
            time.sleep(30)

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
