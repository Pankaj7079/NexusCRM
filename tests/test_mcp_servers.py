"""Tests for Model Context Protocol (MCP) Servers."""

import pytest
from httpx import AsyncClient, ASGITransport

from nexuscrm.mcp_servers.crm_server import app as crm_app
from nexuscrm.mcp_servers.email_server import app as email_app
from nexuscrm.mcp_servers.search_server import app as search_app
from nexuscrm.mcp_servers.analytics_server import app as analytics_app


@pytest.mark.asyncio
async def test_mcp_crm_server():
    """Test MCP CRM tool discovery and tool call execution."""
    async with AsyncClient(transport=ASGITransport(app=crm_app), base_url="http://test") as client:
        # Discovery
        disc_resp = await client.get("/tools")
        assert disc_resp.status_code == 200
        tools = disc_resp.json()["tools"]
        assert len(tools) == 5

        # Call get_contact tool
        call_resp = await client.post(
            "/call",
            json={"name": "get_contact", "arguments": {"identifier": "test@example.com"}},
        )
        assert call_resp.status_code == 200
        res = call_resp.json()["result"]
        assert res["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_mcp_email_server():
    """Test MCP Email draft_email tool."""
    async with AsyncClient(transport=ASGITransport(app=email_app), base_url="http://test") as client:
        call_resp = await client.post(
            "/call",
            json={
                "name": "draft_email",
                "arguments": {"recipient_email": "ceo@acme.com", "subject_intent": "Enterprise Renewal"},
            },
        )
        assert call_resp.status_code == 200
        res = call_resp.json()["result"]
        assert res["recipient"] == "ceo@acme.com"
        assert "Enterprise Renewal" in res["subject"]


@pytest.mark.asyncio
async def test_mcp_analytics_server():
    """Test MCP Analytics predict_churn_risk tool."""
    async with AsyncClient(transport=ASGITransport(app=analytics_app), base_url="http://test") as client:
        call_resp = await client.post(
            "/call",
            json={"name": "predict_churn_risk", "arguments": {"contact_id": "cnt-777"}},
        )
        assert call_resp.status_code == 200
        res = call_resp.json()["result"]
        assert res["contact_id"] == "cnt-777"
        assert "churn_risk_score" in res
