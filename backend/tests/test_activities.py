import pytest
from httpx import AsyncClient

from clara.auth.models import Vault

pytestmark = pytest.mark.asyncio


async def test_activity_type_crud(authenticated_client: AsyncClient, vault: Vault):
    # Create
    resp = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/activities/types",
        json={"name": "Call"},
    )
    assert resp.status_code == 201
    type_id = resp.json()["id"]

    # List
    resp = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/activities/types"
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Update
    resp = await authenticated_client.patch(
        f"/api/v1/vaults/{vault.id}/activities/types/{type_id}",
        json={"name": "Phone Call"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Phone Call"

    # Delete
    resp = await authenticated_client.delete(
        f"/api/v1/vaults/{vault.id}/activities/types/{type_id}"
    )
    assert resp.status_code == 204


async def test_activity_crud(authenticated_client: AsyncClient, vault: Vault):
    # Create
    resp = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/activities",
        json={"title": "Lunch meeting", "happened_at": "2026-02-18T12:00:00"},
    )
    assert resp.status_code == 201
    activity_id = resp.json()["id"]

    # List
    resp = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/activities"
    )
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Get
    resp = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/activities/{activity_id}"
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Lunch meeting"

    # Update
    resp = await authenticated_client.patch(
        f"/api/v1/vaults/{vault.id}/activities/{activity_id}",
        json={"title": "Dinner meeting"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Dinner meeting"

    # Delete
    resp = await authenticated_client.delete(
        f"/api/v1/vaults/{vault.id}/activities/{activity_id}"
    )
    assert resp.status_code == 204

    # Verify gone
    resp = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/activities"
    )
    ids = {item["id"] for item in resp.json()["items"]}
    assert activity_id not in ids
