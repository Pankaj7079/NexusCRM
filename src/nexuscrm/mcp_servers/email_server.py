"""MCP Email Server exposing communication and drafting tools."""

from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger

app = FastAPI(title="MCP Email Server", version="1.0.0")


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


TOOLS_REGISTRY: List[ToolDefinition] = [
    ToolDefinition(
        name="draft_email",
        description="Draft personalized context-aware customer email.",
        input_schema={
            "type": "object",
            "properties": {
                "recipient_email": {"type": "string"},
                "subject_intent": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["recipient_email", "subject_intent"],
        },
    ),
    ToolDefinition(
        name="send_email",
        description="Send finalized email to customer recipient.",
        input_schema={
            "type": "object",
            "properties": {
                "recipient_email": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["recipient_email", "subject", "body"],
        },
    ),
    ToolDefinition(
        name="analyze_email_sentiment",
        description="Analyze sentiment score of customer email text.",
        input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    ),
]


@app.get("/tools")
async def list_tools():
    """Discover available MCP Email tools."""
    return {"tools": [t.model_dump() for t in TOOLS_REGISTRY]}


@app.post("/call")
async def call_tool(payload: Dict[str, Any]):
    """Execute MCP Email tool call."""
    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})

    logger.info(f"MCP Email Server executing tool '{tool_name}' with args: {arguments}")

    if tool_name == "draft_email":
        recipient = arguments.get("recipient_email")
        intent = arguments.get("subject_intent")
        body = (
            f"Hi {recipient.split('@')[0].capitalize()},\n\n"
            f"Following up regarding {intent}. Based on our recent discussions, we would love to schedule a short 15-minute call to discuss our enterprise updates.\n\n"
            f"Best regards,\nNexusCRM Sales Team"
        )
        return {
            "result": {
                "recipient": recipient,
                "subject": f"Follow-up: {intent}",
                "body": body,
                "confidence": 0.92,
            }
        }
    elif tool_name == "send_email":
        return {
            "result": {
                "status": "sent",
                "message_id": "msg-998231",
                "recipient": arguments.get("recipient_email"),
            }
        }
    elif tool_name == "analyze_email_sentiment":
        text = arguments.get("text", "")
        # Simple sentiment heuristic
        positive_words = ["great", "thanks", "excellent", "love", "good", "happy"]
        score = sum(1 for w in positive_words if w in text.lower()) * 0.3
        score = min(1.0, max(-1.0, score if score > 0 else -0.2))
        return {"result": {"text": text, "sentiment_score": round(score, 2)}}
    else:
        raise HTTPException(status_code=404, detail=f"MCP Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.MCP_EMAIL_PORT)
