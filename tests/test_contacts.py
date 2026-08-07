"""Tests for Contacts API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_and_list_contacts(client, auth_headers):
    """Test contact CRUD operations."""
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@acme.com",
        "phone": "+1-555-0199",
        "job_title": "VP of Sales",
        "lead_status": "qualified",
    }
    create_resp = await client.post("/api/v1/contacts", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    contact_data = create_resp.json()
    assert contact_data["first_name"] == "Jane"
    contact_id = contact_data["id"]

    # List contacts
    list_resp = await client.get("/api/v1/contacts", headers=auth_headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1

    # Get contact by ID
    get_resp = await client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "jane.doe@acme.com"
