"""Tests for Multi-Agent System (LangGraph Orchestrator, A2A Protocol, HITL Gates)."""

import pytest


@pytest.mark.asyncio
async def test_agent_orchestrator_execution(client, auth_headers):
    """Test full LangGraph execution flow."""
    exec_payload = {
        "query": "Draft a follow-up email for the enterprise contract renewal",
        "contact_email": "vp.sales@enterprise.com",
        "deal_title": "Enterprise Renewal Deal",
    }

    response = await client.post("/api/v1/agents/execute", json=exec_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["intent"] == "sales_workflow"
    assert data["hitl_pending"] is True
    assert len(data["execution_steps"]) >= 4

    task_id = data["task_id"]

    # Resolve HITL Approval Gate
    approve_payload = {
        "task_id": task_id,
        "approved": True,
        "edited_content": "Final approved proposal body text.",
    }
    approve_resp = await client.post("/api/v1/agents/approve", json=approve_payload, headers=auth_headers)
    assert approve_resp.status_code == 200
    app_data = approve_resp.json()
    assert app_data["status"] == "approved"
    assert "Approved & Dispatched" in app_data["final_response"]
