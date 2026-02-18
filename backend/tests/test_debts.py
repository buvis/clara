import pytest
from httpx import AsyncClient

from clara.auth.models import Vault

pytestmark = pytest.mark.asyncio


async def _create_contact(client: AsyncClient, vault_id) -> str:
    resp = await client.post(
        f"/api/v1/vaults/{vault_id}/contacts",
        json={"first_name": "DebtBuddy"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_debt_crud(authenticated_client: AsyncClient, vault: Vault):
    contact_id = await _create_contact(authenticated_client, vault.id)

    # Create
    resp = await authenticated_client.post(
        f"/api/v1/vaults/{vault.id}/debts",
        json={
            "contact_id": contact_id,
            "direction": "owed",
            "amount": "50.00",
        },
    )
    assert resp.status_code == 201
    debt_id = resp.json()["id"]

    # List
    resp = await authenticated_client.get(f"/api/v1/vaults/{vault.id}/debts")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1

    # Get
    resp = await authenticated_client.get(
        f"/api/v1/vaults/{vault.id}/debts/{debt_id}"
    )
    assert resp.status_code == 200

    # Update
    resp = await authenticated_client.patch(
        f"/api/v1/vaults/{vault.id}/debts/{debt_id}",
        json={"settled": True},
    )
    assert resp.status_code == 200
    assert resp.json()["settled"] is True

    # Delete
    resp = await authenticated_client.delete(
        f"/api/v1/vaults/{vault.id}/debts/{debt_id}"
    )
    assert resp.status_code == 204
