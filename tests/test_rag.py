"""Tests for RAG Engine & RAGAS evaluation."""

import pytest


@pytest.mark.asyncio
async def test_rag_query_and_documents(client, auth_headers):
    """Test RAG document listing and querying."""
    docs_resp = await client.get("/api/v1/rag/documents", headers=auth_headers)
    assert docs_resp.status_code == 200
    docs = docs_resp.json()
    assert len(docs) >= 1

    # Query RAG Engine
    query_resp = await client.post(
        "/api/v1/rag/query",
        json={"query": "What are the enterprise pricing tiers and discounts?"},
        headers=auth_headers,
    )
    assert query_resp.status_code == 200
    data = query_resp.json()
    assert "retrieved_nodes" in data
    assert len(data["retrieved_nodes"]) > 0
    assert data["faithfulness_score"] > 0.5


@pytest.mark.asyncio
async def test_ragas_evaluation(client, auth_headers):
    """Test RAGAS metric evaluation endpoint."""
    eval_payload = {
        "query": "What is the P1 support response time?",
        "contexts": ["Priority P1 (Critical): Response within 15 minutes. Resolution within 4 hours."],
        "answer": "P1 critical support tickets have a 15 minute response time guarantee.",
    }
    eval_resp = await client.post("/api/v1/rag/evaluate", json=eval_payload, headers=auth_headers)
    assert eval_resp.status_code == 200
    res = eval_resp.json()
    assert res["faithfulness_score"] >= 0.7
    assert res["overall_ragas_score"] >= 0.7
    assert res["passed"] is True
