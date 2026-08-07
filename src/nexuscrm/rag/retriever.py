"""Hybrid Retrieval Engine implementing Reciprocal Rank Fusion (RRF)."""

from typing import List, Dict
from llama_index.core.schema import NodeWithScore

from nexuscrm.rag.indexer import vector_store, bm25_store
from nexuscrm.core.logging import logger


class HybridRetriever:
    """Hybrid Retriever fusing dense vector search and sparse BM25 keyword search via Reciprocal Rank Fusion."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def retrieve(self, query: str, top_k: int = 5) -> List[NodeWithScore]:
        """Perform hybrid retrieval with Reciprocal Rank Fusion (RRF)."""
        dense_results = vector_store.search(query, top_k=top_k * 2)
        sparse_results = bm25_store.search(query, top_k=top_k * 2)

        # RRF Scoring Map: node_id -> rrf_score
        rrf_scores: Dict[str, float] = {}
        node_map: Dict[str, NodeWithScore] = {}

        # Process dense results
        for rank, res in enumerate(dense_results):
            node_id = res.node.node_id
            node_map[node_id] = res
            score = 1.0 / (self.rrf_k + (rank + 1))
            rrf_scores[node_id] = rrf_scores.get(node_id, 0.0) + score

        # Process sparse results
        for rank, res in enumerate(sparse_results):
            node_id = res.node.node_id
            node_map[node_id] = res
            score = 1.0 / (self.rrf_k + (rank + 1))
            rrf_scores[node_id] = rrf_scores.get(node_id, 0.0) + score

        # Sort combined nodes by RRF score
        sorted_node_ids = sorted(rrf_scores.keys(), key=lambda nid: rrf_scores[nid], reverse=True)

        final_nodes: List[NodeWithScore] = []
        for nid in sorted_node_ids[:top_k]:
            original_node = node_map[nid]
            final_nodes.append(
                NodeWithScore(node=original_node.node, score=round(rrf_scores[nid], 4))
            )

        logger.info(f"HybridRetriever retrieved {len(final_nodes)} fused nodes for query: '{query}'")
        return final_nodes


hybrid_retriever = HybridRetriever()
