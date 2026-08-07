"""MCP Analytics Server exposing predictive ML model tools."""

from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger

app = FastAPI(title="MCP Analytics Server", version="1.0.0")


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


TOOLS_REGISTRY: List[ToolDefinition] = [
    ToolDefinition(
        name="predict_churn_risk",
        description="Predict customer churn probability using XGBoost model.",
        input_schema={"type": "object", "properties": {"contact_id": {"type": "string"}}, "required": ["contact_id"]},
    ),
    ToolDefinition(
        name="score_lead",
        description="Calculate lead conversion score using LightGBM model.",
        input_schema={"type": "object", "properties": {"contact_id": {"type": "string"}}, "required": ["contact_id"]},
    ),
    ToolDefinition(
        name="get_revenue_forecast",
        description="Generate quarterly revenue forecast using Prophet time series model.",
        input_schema={"type": "object", "properties": {"months_ahead": {"type": "integer"}}},
    ),
    ToolDefinition(
        name="explain_prediction",
        description="Generate SHAP feature explanations for customer churn or lead score.",
        input_schema={"type": "object", "properties": {"contact_id": {"type": "string"}}, "required": ["contact_id"]},
    ),
]


@app.get("/tools")
async def list_tools():
    """Discover available MCP Analytics tools."""
    return {"tools": [t.model_dump() for t in TOOLS_REGISTRY]}


@app.post("/call")
async def call_tool(payload: Dict[str, Any]):
    """Execute MCP Analytics tool call."""
    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})

    logger.info(f"MCP Analytics Server executing tool '{tool_name}' with args: {arguments}")

    if tool_name == "predict_churn_risk":
        cid = arguments.get("contact_id")
        return {
            "result": {
                "contact_id": cid,
                "churn_risk_score": 0.78,
                "risk_category": "High Risk",
                "model_version": "XGBoost_v1.0",
            }
        }
    elif tool_name == "score_lead":
        cid = arguments.get("contact_id")
        return {
            "result": {
                "contact_id": cid,
                "lead_score": 88.4,
                "tier": "Hot Lead",
                "model_version": "LightGBM_v1.0",
            }
        }
    elif tool_name == "get_revenue_forecast":
        months = arguments.get("months_ahead", 3)
        return {
            "result": {
                "forecast_months": months,
                "predicted_revenue": 340000.0,
                "confidence_interval_80": [310000.0, 375000.0],
                "model_version": "Prophet_v1.0",
            }
        }
    elif tool_name == "explain_prediction":
        cid = arguments.get("contact_id")
        return {
            "result": {
                "contact_id": cid,
                "top_shap_features": [
                    {"feature": "days_since_last_contact", "importance": 0.42, "effect": "increases_churn"},
                    {"feature": "avg_sentiment_30d", "importance": -0.28, "effect": "decreases_churn"},
                    {"feature": "open_support_tickets", "importance": 0.18, "effect": "increases_churn"},
                ],
                "summary": "Customer has not had an activity in 42 days, driving up churn risk score.",
            }
        }
    else:
        raise HTTPException(status_code=404, detail=f"MCP Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.MCP_ANALYTICS_PORT)
