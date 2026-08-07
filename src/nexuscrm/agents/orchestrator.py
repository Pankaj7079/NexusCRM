"""LangGraph Orchestrator managing multi-agent workflows, state checkpoints, and HITL gates."""

import uuid
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger
from nexuscrm.agents.a2a_client import a2a_client, A2ATaskPayload
from nexuscrm.agents.harness import memory_manager
from nexuscrm.core.llm_guardrails import llm_guardrails
from nexuscrm.core.token_tracker import token_tracker


class AgentState(TypedDict):
    task_id: str
    user_query: str
    contact_email: Optional[str]
    deal_title: Optional[str]
    intent: Optional[str]
    memory_context: Dict[str, Any]
    guardrail_passed: bool
    hitl_pending: bool
    hitl_approved: Optional[bool]
    crew_output: Optional[Dict[str, Any]]
    final_response: Optional[str]
    execution_steps: List[str]


async def memory_loader_node(state: AgentState) -> AgentState:
    """Step 1: Load 4-tier memory system (Short, Episodic, Long-term facts, Semantic RAG)."""
    token_tracker.enforce_rate_delay()  # Polite rate limit delay between API calls
    logger.info(f"LangGraph Node [memory_loader] executing for query: '{state['user_query']}'")
    steps = list(state.get("execution_steps", []))

    memory_ctx = memory_manager.load_context(state.get("contact_email"))
    steps.append(f"Memory Harness: Loaded {len(memory_ctx['long_term_facts'])} long-term facts & episodic history.")

    return {
        **state,
        "memory_context": memory_ctx,
        "execution_steps": steps,
    }


async def guardrail_check_node(state: AgentState) -> AgentState:
    """Step 2: Senior LLM Guardrails scan (PII, Prompt Injection, Token Budget Check)."""
    logger.info("LangGraph Node [guardrail_check] executing multi-layer LLM guardrail scan.")
    steps = list(state.get("execution_steps", []))

    scan_result = llm_guardrails.validate_input(state["user_query"])
    if not scan_result.is_safe:
        steps.append(f"LLM Guardrail Blocked: {', '.join(scan_result.violations)}")
        return {
            **state,
            "guardrail_passed": False,
            "final_response": f"Request blocked by Senior LLM Safety Guardrail: {scan_result.violations[0]}",
            "execution_steps": steps,
        }

    steps.append(f"LLM Guardrail: Input validation, PII scan & token budget check ({scan_result.input_tokens} tokens) passed.")
    return {
        **state,
        "guardrail_passed": True,
        "user_query": scan_result.sanitized_text,
        "execution_steps": steps,
    }




async def intent_classifier_node(state: AgentState) -> AgentState:
    """Step 3: Classify user request intent into sales vs support vs analytics workflow."""
    logger.info("LangGraph Node [intent_classifier] determining workflow route.")
    steps = list(state.get("execution_steps", []))

    query = state["user_query"].lower()
    if any(k in query for k in ["email", "draft", "lead", "deal", "pricing", "sales"]):
        intent = "sales_workflow"
    elif any(k in query for k in ["ticket", "support", "help", "bug", "issue", "sla"]):
        intent = "support_workflow"
    else:
        intent = "sales_workflow"

    steps.append(f"Intent Classifier: Classified intent as '{intent}'.")
    return {
        **state,
        "intent": intent,
        "execution_steps": steps,
    }


async def sales_crew_node(state: AgentState) -> AgentState:
    """Step 4a: Delegate to CrewAI Sales Crew via Google A2A Protocol."""
    logger.info("LangGraph Node [sales_crew] delegating via A2A protocol.")
    steps = list(state.get("execution_steps", []))

    payload = A2ATaskPayload(
        task_id=state["task_id"],
        task_type="email_draft",
        context={
            "contact_email": state.get("contact_email") or "client@acme.com",
            "deal_title": state.get("deal_title") or "Enterprise Renewal",
            "user_query": state["user_query"],
        },
    )

    a2a_url = f"http://localhost:{settings.A2A_SALES_PORT}"
    result = await a2a_client.send_task(a2a_url, payload)

    steps.append("A2A Delegation: CrewAI Sales Crew executed draft email task.")

    requires_hitl = result.output.get("requires_hitl_approval", True)

    return {
        **state,
        "crew_output": result.output,
        "hitl_pending": requires_hitl,
        "execution_steps": steps,
    }


async def support_crew_node(state: AgentState) -> AgentState:
    """Step 4b: Delegate to CrewAI Support Crew via Google A2A Protocol."""
    logger.info("LangGraph Node [support_crew] delegating via A2A protocol.")
    steps = list(state.get("execution_steps", []))

    payload = A2ATaskPayload(
        task_id=state["task_id"],
        task_type="knowledge_query",
        context={
            "contact_email": state.get("contact_email") or "user@company.com",
            "subject": state["user_query"],
        },
    )

    a2a_url = f"http://localhost:{settings.A2A_SUPPORT_PORT}"
    result = await a2a_client.send_task(a2a_url, payload)

    steps.append("A2A Delegation: CrewAI Support Crew executed ticket resolution task.")

    return {
        **state,
        "crew_output": result.output,
        "hitl_pending": False,
        "execution_steps": steps,
    }


async def response_formatter_node(state: AgentState) -> AgentState:
    """Step 5: Format final result payload."""
    logger.info("LangGraph Node [response_formatter] compiling execution summary.")
    steps = list(state.get("execution_steps", []))

    if state.get("hitl_pending") and state.get("hitl_approved") is not True:
        resp = "Workflow paused at HITL Gate: Draft email generated and awaiting human manager approval."
        steps.append("HITL Gate: Paused for human verification.")
    else:
        crew_out = state.get("crew_output", {})
        resp = crew_out.get("draft_body") or crew_out.get("suggested_solution") or "Task executed successfully."
        steps.append("Execution Complete: Formatted response delivered.")

    return {
        **state,
        "final_response": resp,
        "execution_steps": steps,
    }


def route_intent(state: AgentState) -> str:
    """Router decision logic."""
    if not state.get("guardrail_passed", True):
        return "response_formatter"
    if state.get("intent") == "support_workflow":
        return "support_crew"
    return "sales_crew"


# Build LangGraph Workflow DAG
workflow = StateGraph(AgentState)
workflow.add_node("memory_loader", memory_loader_node)
workflow.add_node("guardrail_check", guardrail_check_node)
workflow.add_node("intent_classifier", intent_classifier_node)
workflow.add_node("sales_crew", sales_crew_node)
workflow.add_node("support_crew", support_crew_node)
workflow.add_node("response_formatter", response_formatter_node)

# Set Graph Edges
workflow.set_entry_point("memory_loader")
workflow.add_edge("memory_loader", "guardrail_check")
workflow.add_edge("guardrail_check", "intent_classifier")
workflow.add_conditional_edges("intent_classifier", route_intent)
workflow.add_edge("sales_crew", "response_formatter")
workflow.add_edge("support_crew", "response_formatter")
workflow.add_edge("response_formatter", END)

# Compile Orchestrator App
agent_orchestrator = workflow.compile()
