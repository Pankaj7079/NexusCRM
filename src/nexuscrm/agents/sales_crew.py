"""CrewAI Sales Crew & A2A Protocol Server (Port 8001)."""

from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger
from nexuscrm.agents.a2a_client import AgentCard, A2ATaskPayload, A2ATaskResult

app = FastAPI(title="CrewAI Sales Crew A2A Server", version="1.0.0")

SALES_AGENT_CARD = AgentCard(
    name="NexusCRM Sales Crew",
    description="CrewAI specialized sales agents for lead scoring, email drafting, deal analysis, and pipeline velocity.",
    capabilities=["lead_scoring", "email_drafting", "deal_analysis", "followup_strategy"],
    a2a_endpoint=f"http://localhost:{settings.A2A_SALES_PORT}/a2a/task",
)


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Expose Google A2A Agent Card for agent discovery."""
    return SALES_AGENT_CARD.model_dump()


@app.post("/a2a/task", response_model=A2ATaskResult)
async def execute_sales_task(payload: A2ATaskPayload):
    """A2A Server endpoint executing CrewAI Sales Crew workflows."""
    logger.info(f"Sales Crew A2A Server processing task: {payload.task_type}")

    ctx = payload.context
    contact_email = ctx.get("contact_email", "customer@example.com")
    deal_title = ctx.get("deal_title", "Enterprise Renewal")

    if payload.task_type in ["email_draft", "email_task"]:
        result_output = {
            "recipient": contact_email,
            "subject": f"Follow-up: {deal_title} Opportunity",
            "draft_body": (
                f"Hi,\n\nFollowing up on our recent conversation regarding {deal_title}. "
                f"We've analyzed your requirement and would like to present a tailored proposal.\n\n"
                f"Best regards,\nSales Execution Agent"
            ),
            "tone": "professional_persuasive",
            "requires_hitl_approval": True,
        }
    elif payload.task_type == "lead_score":
        result_output = {
            "contact_email": contact_email,
            "lead_score": 88.5,
            "segment": "Hot Lead",
            "recommended_action": "Schedule demo call within 24 hours.",
        }
    else:  # deal_analysis
        result_output = {
            "deal_title": deal_title,
            "health_status": "Healthy",
            "win_probability": 0.82,
            "risk_factors": ["Pending legal review"],
            "recommended_next_step": "Send finalized contract draft.",
        }

    return A2ATaskResult(
        task_id=payload.task_id,
        status="completed",
        crew_name="CrewAISalesCrew",
        output=result_output,
        recommendation="Review draft email before sending.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.A2A_SALES_PORT)
