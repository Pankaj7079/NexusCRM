"""RAG Knowledge Base API Router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pydantic import BaseModel

from nexuscrm.api.auth import get_current_user
from nexuscrm.models.user import User
from nexuscrm.rag.indexer import PageIndexChunker, vector_store, bm25_store, global_document_registry
from nexuscrm.rag.retriever import hybrid_retriever
from nexuscrm.rag.evaluator import ragas_evaluator, RAGASEvalRequest, RAGASEvalResponse

router = APIRouter(prefix="/rag", tags=["RAG Engine"])


class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class RAGQueryResultNode(BaseModel):
    text: str
    score: float
    filename: str
    page_number: int


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_nodes: List[RAGQueryResultNode]
    faithfulness_score: float


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    query_in: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Query knowledge base using LlamaIndex PageIndex hybrid retrieval engine."""
    results = hybrid_retriever.retrieve(query_in.query, top_k=query_in.top_k or 5)

    nodes_out = []
    contexts = []
    for res in results:
        text_content = res.node.get_content()
        contexts.append(text_content)
        nodes_out.append(
            RAGQueryResultNode(
                text=text_content,
                score=round(float(res.score), 4),
                filename=res.node.metadata.get("filename", "unknown"),
                page_number=res.node.metadata.get("page_number", 1),
            )
        )

    # Synthesize structured response
    synthesized_answer = (
        f"Based on internal knowledge documents ({', '.join(set(n.filename for n in nodes_out))}):\n"
        + (contexts[0] if contexts else "No relevant context found.")
    )

    eval_result = ragas_evaluator.evaluate(
        RAGASEvalRequest(query=query_in.query, contexts=contexts, answer=synthesized_answer)
    )

    return RAGQueryResponse(
        query=query_in.query,
        answer=synthesized_answer,
        retrieved_nodes=nodes_out,
        faithfulness_score=eval_result.faithfulness_score,
    )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload PDF/Markdown document for RAG PageIndex ingestion."""
    content_bytes = await file.read()
    content_str = content_bytes.decode("utf-8", errors="ignore")

    nodes = PageIndexChunker.chunk_document(content_str, file.filename)
    vector_store.add_nodes(nodes)
    bm25_store.index_nodes(vector_store.nodes)

    doc_meta = {
        "id": file.filename,
        "filename": file.filename,
        "chunk_count": len(nodes),
        "status": "indexed",
    }
    global_document_registry.append(doc_meta)

    return {"message": "Document ingested successfully", "document": doc_meta}


@router.get("/documents")
async def list_documents(current_user: User = Depends(get_current_user)):
    """List indexed RAG documents."""
    return global_document_registry


@router.post("/evaluate", response_model=RAGASEvalResponse)
async def evaluate_rag(
    eval_in: RAGASEvalRequest,
    current_user: User = Depends(get_current_user),
):
    """Run RAGAS evaluation metrics on query/answer context triplet."""
    return ragas_evaluator.evaluate(eval_in)
