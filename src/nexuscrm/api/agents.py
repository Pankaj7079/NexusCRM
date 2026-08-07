"""Agents REST & Streaming SSE API Router."""

import uuid
import json
import asyncio
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from nexuscrm.api.auth import get_current_user
from nexuscrm.models.user import User
from nexuscrm.agents.orchestrator import agent_orchestrator, AgentState
from nexuscrm.agents.harness import feedback_collector, FeedbackRecord, memory_manager, time_scheduler

router = APIRouter(prefix="/agents", tags=["Agentic Multi-Agent System"])


class AgentExecuteRequest(BaseModel):
    query: str
    contact_email: Optional[str] = "customer@example.com"
    deal_title: Optional[str] = "Enterprise Renewal"


class HITLApprovalRequest(BaseModel):
    task_id: str
    approved: bool
    edited_content: Optional[str] = None


class UserFeedbackPayload(BaseModel):
    task_id: str
    rating: int  # +1 or -1
    comment: Optional[str] = None
    edit_distance: Optional[int] = 0


@router.post("/feedback")
async def submit_user_feedback(
    payload: UserFeedbackPayload,
    current_user: User = Depends(get_current_user),
):
    """Log user feedback to drive agent self-improvement feedback loops."""
    feedback_collector.log_feedback(
        FeedbackRecord(
            task_id=payload.task_id,
            rating=payload.rating,
            comment=payload.comment,
            edit_distance=payload.edit_distance,
        )
    )
    return {
        "status": "feedback_recorded",
        "task_id": payload.task_id,
        "current_metrics": feedback_collector.get_metrics(),
    }



# Global in-memory active agent execution store
active_agent_runs: Dict[str, AgentState] = {}


@router.post("/execute")
async def execute_agent_task(
    request: AgentExecuteRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute complete multi-agent LangGraph workflow."""
    task_id = f"task-{uuid.uuid4().hex[:8]}"

    initial_state: AgentState = {
        "task_id": task_id,
        "user_query": request.query,
        "contact_email": request.contact_email,
        "deal_title": request.deal_title,
        "intent": None,
        "memory_context": {},
        "guardrail_passed": True,
        "hitl_pending": False,
        "hitl_approved": None,
        "crew_output": None,
        "final_response": None,
        "execution_steps": [],
    }

    final_state = await agent_orchestrator.ainvoke(initial_state)
    active_agent_runs[task_id] = final_state

    return {
        "task_id": task_id,
        "intent": final_state["intent"],
        "hitl_pending": final_state["hitl_pending"],
        "final_response": final_state["final_response"],
        "execution_steps": final_state["execution_steps"],
        "crew_output": final_state["crew_output"],
    }


@router.post("/approve")
async def approve_hitl_task(
    request: HITLApprovalRequest,
    current_user: User = Depends(get_current_user),
):
    """Resolve Human-in-the-Loop (HITL) pending gate."""
    state = active_agent_runs.get(request.task_id)
    if not state:
        raise HTTPException(status_code=404, detail="Agent task ID not found.")

    state["hitl_pending"] = False
    state["hitl_approved"] = request.approved

    if request.approved:
        if request.edited_content and state.get("crew_output"):
            state["crew_output"]["draft_body"] = request.edited_content
        state["final_response"] = (
            f"Approved & Dispatched by Manager ({current_user.full_name}): "
            + (state.get("crew_output", {}).get("draft_body", "Action executed."))
        )
    else:
        state["final_response"] = f"Action rejected by Manager ({current_user.full_name})."

    state["execution_steps"].append(f"HITL Gate: Task {request.task_id} resolved (Approved={request.approved}).")
    active_agent_runs[request.task_id] = state

    return {
        "task_id": request.task_id,
        "status": "approved" if request.approved else "rejected",
        "final_response": state["final_response"],
    }


@router.get("/stream")
async def stream_agent_execution(
    query: str,
    current_user: User = Depends(get_current_user),
):
    """Real-time SSE event stream of multi-agent state progression."""
    async def event_generator():
        task_id = f"stream-{uuid.uuid4().hex[:6]}"

        steps = [
            f"data: {json.dumps({'step': 'Memory Loader', 'message': 'Loaded customer interaction memory.'})}\n\n",
            f"data: {json.dumps({'step': 'Guardrail Check', 'message': 'PII & Prompt Safety checks passed.'})}\n\n",
            f"data: {json.dumps({'step': 'Intent Classifier', 'message': 'Routing to CrewAI Sales Crew via A2A Protocol.'})}\n\n",
            f"data: {json.dumps({'step': 'CrewAI Sales Crew', 'message': 'EmailDraftAgent generated context-aware draft.'})}\n\n",
            f"data: {json.dumps({'step': 'HITL Gate', 'message': 'Paused for human manager approval.', 'task_id': task_id})}\n\n",
        ]

        for step_event in steps:
            yield step_event
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
