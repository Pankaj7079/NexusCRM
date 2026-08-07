"""MCP CRM Server exposing CRM CRUD tools via Model Context Protocol standard."""

from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger

app = FastAPI(title="MCP CRM Server", version="1.0.0")


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


TOOLS_REGISTRY: List[ToolDefinition] = [
    ToolDefinition(
        name="get_contact",
        description="Fetch customer contact record by email or ID.",
        input_schema={"type": "object", "properties": {"identifier": {"type": "string"}}, "required": ["identifier"]},
    ),
    ToolDefinition(
        name="search_contacts",
        description="Search customer contacts by query string.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    ),
    ToolDefinition(
        name="get_deal",
        description="Retrieve deal details by deal title or ID.",
        input_schema={"type": "object", "properties": {"deal_id": {"type": "string"}}, "required": ["deal_id"]},
    ),
    ToolDefinition(
        name="update_deal_stage",
        description="Update deal pipeline stage.",
        input_schema={
            "type": "object",
            "properties": {"deal_id": {"type": "string"}, "stage": {"type": "string"}},
            "required": ["deal_id", "stage"],
        },
    ),
    ToolDefinition(
        name="get_pipeline_status",
        description="Retrieve overall revenue pipeline summary.",
        input_schema={"type": "object", "properties": {}},
    ),
]


@app.get("/tools")
async def list_tools():
    """Discover available MCP CRM tools."""
    return {"tools": [t.model_dump() for t in TOOLS_REGISTRY]}


@app.post("/call")
async def call_tool(payload: Dict[str, Any]):
    """Execute an MCP tool call by name."""
    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})

    logger.info(f"MCP CRM Server executing tool '{tool_name}' with args: {arguments}")

    if tool_name == "get_contact":
        return {
            "result": {
                "id": "cnt-12345",
                "first_name": "Sarah",
                "last_name": "Conner",
                "email": arguments.get("identifier"),
                "lead_score": 85.5,
                "churn_risk": 0.12,
            }
        }
    elif tool_name == "search_contacts":
        return {
            "result": [
                {"id": "cnt-1", "first_name": "Alice", "email": "alice@acme.com", "lead_score": 90.0},
                {"id": "cnt-2", "first_name": "Bob", "email": "bob@globex.com", "lead_score": 72.0},
            ]
        }
    elif tool_name == "get_deal":
        return {
            "result": {
                "id": arguments.get("deal_id"),
                "title": "Enterprise Cloud Migration Deal",
                "value": 120000.0,
                "stage": "negotiation",
                "win_probability": 0.8,
            }
        }
    elif tool_name == "update_deal_stage":
        return {
            "result": {
                "deal_id": arguments.get("deal_id"),
                "new_stage": arguments.get("stage"),
                "status": "updated",
            }
        }
    elif tool_name == "get_pipeline_status":
        return {
            "result": {
                "total_pipeline_value": 450000.0,
                "open_deals_count": 14,
                "weighted_forecast": 310000.0,
            }
        }
    else:
        raise HTTPException(status_code=404, detail=f"MCP Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.MCP_CRM_PORT)
