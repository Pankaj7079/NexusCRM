"""Document Ingestion Service using LlamaIndex and PageIndex strategy."""

import os
import re
from typing import List, Dict, Any, Optional
from llama_index.core.schema import TextNode, NodeWithScore
from rank_bm25 import BM25Okapi

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger


class PageIndexChunker:
    """PageIndex Strategy: Parses raw text/markdown into page-bounded nodes with page metadata."""

    @staticmethod
    def chunk_document(text: str, filename: str) -> List[TextNode]:
        """Split document by explicit page markers or logical paragraph blocks."""
        nodes: List[TextNode] = []
        # Check for explicit Page markers (e.g. --- Page 1 --- or \f)
        pages = re.split(r'(?:\f|---+ Page \d+ ---+)', text)
        if len(pages) <= 1:
            # Fallback: group into ~500 word page blocks
            words = text.split()
            page_size = 400
            pages = [' '.join(words[i:i + page_size]) for i in range(0, len(words), page_size)]

        for idx, page_text in enumerate(pages):
            page_content = page_text.strip()
            if not page_content:
                continue
            node = TextNode(
                text=page_content,
                metadata={
                    "filename": filename,
                    "page_number": idx + 1,
                    "index_strategy": "page_index",
                },
            )
            nodes.append(node)
        return nodes


class LocalMemoryVectorStore:
    """Lightweight in-memory vector store with TF-IDF/Cosine fallback when external vector DB is offline."""

    def __init__(self):
        self.nodes: List[TextNode] = []

    def add_nodes(self, nodes: List[TextNode]):
        self.nodes.extend(nodes)

    def clear(self):
        self.nodes.clear()

    def search(self, query: str, top_k: int = 5) -> List[NodeWithScore]:
        query_words = set(query.lower().split())
        scored_nodes = []
        for node in self.nodes:
            node_words = set(node.get_content().lower().split())
            intersection = query_words.intersection(node_words)
            score = len(intersection) / max(len(query_words), 1)
            if score > 0:
                scored_nodes.append(NodeWithScore(node=node, score=score))

        scored_nodes.sort(key=lambda x: x.score, reverse=True)
        return scored_nodes[:top_k]


class BM25RetrieverEngine:
    """Sparse BM25 Keyword Search Engine."""

    def __init__(self):
        self.nodes: List[TextNode] = []
        self.bm25: Optional[BM25Okapi] = None

    def index_nodes(self, nodes: List[TextNode]):
        self.nodes = nodes
        corpus = [node.get_content().lower().split() for node in nodes]
        if corpus:
            self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 5) -> List[NodeWithScore]:
        if not self.bm25 or not self.nodes:
            return []
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append(NodeWithScore(node=self.nodes[idx], score=float(scores[idx])))
        return results


# Global RAG state managers
vector_store = LocalMemoryVectorStore()
bm25_store = BM25RetrieverEngine()
global_document_registry: List[Dict[str, Any]] = []


def register_sample_documents():
    """Register knowledge base documents from data/knowledge_base/ directory or fallback templates."""
    kb_dir = os.path.join("data", "knowledge_base")
    sample_docs = []

    if os.path.exists(kb_dir):
        for fname in sorted(os.listdir(kb_dir)):
            fpath = os.path.join(kb_dir, fname)
            if os.path.isfile(fpath) and fname.endswith((".txt", ".md", ".pdf")):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    sample_docs.append({"filename": fname, "content": content})
                except Exception:
                    pass

    if not sample_docs:
        sample_docs = [
            {
                "filename": "Enterprise_Pricing_Guide_2026.txt",
                "content": """--- Page 1 ---
NexusCRM Enterprise Pricing Guide 2026.
Tier 1: Starter Plan ($49/user/month) - Includes CRM CRUD, Lead Management, Email Integration.
Tier 2: Professional Plan ($99/user/month) - Adds Agentic Harness, RAG Knowledge Base, Churn Risk Model.
Tier 3: Enterprise Custom ($199/user/month) - Multi-Agent A2A Collaboration, Dedicated MCP Servers, Custom ML Models, 24/7 SLA Support.

--- Page 2 ---
Discount Policy: Annual billing grants a 20% flat discount on all tiers.
Refund Policy: 30-day money back guarantee for all enterprise tier contracts.""",
            },
            {
                "filename": "Customer_Support_SLA_and_Escalation.txt",
                "content": """--- Page 1 ---
Support Service Level Agreement (SLA) & Escalation Matrix.
Priority P1 (Critical): Response within 15 minutes. Resolution within 4 hours.
Priority P2 (High): Response within 1 hour. Resolution within 24 hours.
Priority P3 (Normal): Response within 4 hours. Resolution within 48 hours.

--- Page 2 ---
Escalation Pathway: If a P1 support ticket is not resolved within 2 hours, automatically trigger the TicketTriageAgent and alert the Support Operations Manager.""",
            },
        ]

    all_nodes = []
    global_document_registry.clear()
    vector_store.clear()

    for doc in sample_docs:
        nodes = PageIndexChunker.chunk_document(doc["content"], doc["filename"])
        all_nodes.extend(nodes)
        global_document_registry.append({
            "id": doc["filename"],
            "filename": doc["filename"],
            "chunk_count": len(nodes),
            "status": "indexed",
        })

    vector_store.add_nodes(all_nodes)
    bm25_store.index_nodes(all_nodes)
    logger.info(f"RAG Indexer populated with {len(all_nodes)} PageIndex nodes across {len(sample_docs)} documents.")


# Populate initial RAG knowledge base
register_sample_documents()
