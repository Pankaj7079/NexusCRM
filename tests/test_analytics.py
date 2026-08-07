"""Tests for Predictive Analytics API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_analytics_churn_prediction(client, auth_headers):
    """Test XGBoost Churn Risk Prediction endpoint."""
    payload = {
        "days_since_last_contact": 60,
        "activity_count_30d": 1,
        "activity_count_90d": 3,
        "avg_sentiment_30d": -0.6,
        "email_response_rate": 0.2,
        "open_support_tickets": 3,
        "deal_count": 1,
        "deal_win_rate": 0.2,
        "avg_deal_value": 12000.0,
        "days_as_customer": 120,
        "contract_months_remaining": 1,
        "monthly_recurring_revenue": 1200.0,
        "net_promoter_score": 4,
    }
    response = await client.post("/api/v1/analytics/churn/predict", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "churn_risk_score" in data
    assert "risk_category" in data
    assert len(data["top_shap_features"]) > 0


@pytest.mark.asyncio
async def test_analytics_lead_scoring(client, auth_headers):
    """Test LightGBM Lead Scoring endpoint."""
    payload = {
        "days_since_last_contact": 5,
        "activity_count_30d": 12,
        "activity_count_90d": 30,
        "avg_sentiment_30d": 0.8,
        "email_response_rate": 0.9,
        "open_support_tickets": 0,
        "deal_count": 5,
        "deal_win_rate": 0.8,
        "avg_deal_value": 85000.0,
        "days_as_customer": 500,
        "contract_months_remaining": 18,
        "monthly_recurring_revenue": 8500.0,
        "net_promoter_score": 10,
    }
    response = await client.post("/api/v1/analytics/lead/score", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "lead_score" in data
    assert "tier" in data


@pytest.mark.asyncio
async def test_analytics_forecast(client, auth_headers):
    """Test Revenue Forecast endpoint."""
    response = await client.get("/api/v1/analytics/forecast?months=3", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_months"] == 3
    assert "total_projected_revenue" in data
    assert len(data["monthly_breakdown"]) == 3
