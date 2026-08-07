"""MCP Search Server exposing search and RAG tools."""

from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger
from nexuscrm.rag.retriever import hybrid_retriever

app = FastAPI(title="MCP Search Server", version="1.0.0")


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


TOOLS_REGISTRY: List[ToolDefinition] = [
    ToolDefinition(
        name="search_knowledge_base",
        description="Search company internal knowledge documents using LlamaIndex PageIndex RAG.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    ),
    ToolDefinition(
        name="get_company_info",
        description="Lookup external company web details.",
        input_schema={"type": "object", "properties": {"company_name": {"type": "string"}}, "required": ["company_name"]},
    ),
]


@app.get("/tools")
async def list_tools():
    """Discover available MCP Search tools."""
    return {"tools": [t.model_dump() for t in TOOLS_REGISTRY]}


@app.post("/call")
async def call_tool(payload: Dict[str, Any]):
    """Execute MCP Search tool call."""
    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})

    logger.info(f"MCP Search Server executing tool '{tool_name}' with args: {arguments}")

    if tool_name == "search_knowledge_base":
        query = arguments.get("query", "")
        results = hybrid_retriever.retrieve(query, top_k=3)
        retrieved_items = [
            {
                "text": res.node.get_content(),
                "score": round(float(res.score), 4),
                "filename": res.node.metadata.get("filename"),
            }
            for res in results
        ]
        return {"result": {"query": query, "documents": retrieved_items}}
    elif tool_name == "get_company_info":
        comp_name = arguments.get("company_name", "")
        return {
            "result": {
                "company_name": comp_name,
                "industry": "Enterprise Technology",
                "funding_stage": "Series B",
                "employee_range": "250-500",
                "website": f"https://www.{comp_name.lower().replace(' ', '')}.com",
            }
        }
    else:
        raise HTTPException(status_code=404, detail=f"MCP Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.MCP_SEARCH_PORT)
