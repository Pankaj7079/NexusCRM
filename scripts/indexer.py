"""RAG Indexer Script Wrapper."""

from nexuscrm.rag.indexer import register_sample_documents

if __name__ == "__main__":
    print("Indexing RAG Knowledge Base...")
    register_sample_documents()
    print("[SUCCESS] RAG Knowledge Base indexed successfully!")
