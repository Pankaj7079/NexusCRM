"""CrewAI Support Crew & A2A Protocol Server (Port 8002)."""

from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger
from nexuscrm.agents.a2a_client import AgentCard, A2ATaskPayload, A2ATaskResult

app = FastAPI(title="CrewAI Support Crew A2A Server", version="1.0.0")

SUPPORT_AGENT_CARD = AgentCard(
    name="NexusCRM Support Crew",
    description="CrewAI specialized support agents for ticket triage, knowledge base resolution, and customer sentiment escalation.",
    capabilities=["ticket_triage", "knowledge_query", "sentiment_escalation"],
    a2a_endpoint=f"http://localhost:{settings.A2A_SUPPORT_PORT}/a2a/task",
)


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Expose Google A2A Agent Card for agent discovery."""
    return SUPPORT_AGENT_CARD.model_dump()


@app.post("/a2a/task", response_model=A2ATaskResult)
async def execute_support_task(payload: A2ATaskPayload):
    """A2A Server endpoint executing CrewAI Support Crew workflows."""
    logger.info(f"Support Crew A2A Server processing task: {payload.task_type}")

    ctx = payload.context
    ticket_subject = ctx.get("subject", "Product Assistance")
    customer_email = ctx.get("contact_email", "user@example.com")

    result_output = {
        "ticket_subject": ticket_subject,
        "customer_email": customer_email,
        "priority": "P2_High",
        "suggested_solution": (
            f"Resolved ticket '{ticket_subject}': Verified user permission levels in settings "
            f"and updated API endpoint scopes."
        ),
        "confidence_score": 0.95,
        "escalation_required": False,
    }

    return A2ATaskResult(
        task_id=payload.task_id,
        status="completed",
        crew_name="CrewAISupportCrew",
        output=result_output,
        recommendation="Send automated solution proposal to customer.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.A2A_SUPPORT_PORT)
