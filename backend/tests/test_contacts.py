import pytest
from httpx import AsyncClient

from clara.auth.models import Vault

pytestmark = pytest.mark.asyncio


async def test_create_contact(authenticated_client: AsyncClient, vault: Vault):
    response = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "Alice", "last_name": "Smith"},
    )
    assert response.status_code == 201
    assert response.json()["first_name"] == "Alice"


async def test_list_contacts(authenticated_client: AsyncClient, vault: Vault):
    create = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "Bob"},
    )
    assert create.status_code == 201

    response = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/contacts?offset=0&limit=10"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 1
    assert len(body["items"]) == 1


async def test_get_contact(authenticated_client: AsyncClient, vault: Vault):
    create = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "Charlie"},
    )
    assert create.status_code == 201
    contact_id = create.json()["id"]

    response = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/contacts/{contact_id}"
    )
    assert response.status_code == 200
    assert response.json()["id"] == contact_id


async def test_update_contact(authenticated_client: AsyncClient, vault: Vault):
    create = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "Dani"},
    )
    assert create.status_code == 201
    contact_id = create.json()["id"]

    response = await authenticated_client.patch(
        f"/api/v1/vaults/{vault.id}/contacts/{contact_id}",
        json={"first_name": "Danielle", "favorite": True},
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Danielle"
    assert response.json()["favorite"] is True


async def test_delete_contact(authenticated_client: AsyncClient, vault: Vault):
    create = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "Eli"},
    )
    assert create.status_code == 201
    contact_id = create.json()["id"]

    delete = await authenticated_client.delete(
        f"/api/v1/vaults/{vault.id}/contacts/{contact_id}"
    )
    assert delete.status_code == 204

    listed = await authenticated_client.get(f"/api/v1/vaults/{vault.id}/contacts")
    assert listed.status_code == 200
    ids = {item["id"] for item in listed.json()["items"]}
    assert contact_id not in ids


async def test_filter_by_favorites(authenticated_client: AsyncClient, vault: Vault):
    first = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "Fav", "favorite": True},
    )
    second = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/contacts",
        json={"first_name": "NotFav", "favorite": False},
    )
    assert first.status_code == 201
    assert second.status_code == 201

    response = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/contacts?favorites=true"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["favorite"] is True
