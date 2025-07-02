import chromadb
import ollama
from typing import List, Optional, Dict

class RetrievalService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection("legal_documents")

    async def search_similar(self, query: str, folder_id: Optional[int] = None, top_k: int = 5) -> List[Dict]:
        query_embedding = ollama.embeddings(
            model='mxbai-embed-large',
            prompt=query
        )['embedding']
        where_filter = {}
        if folder_id:
            where_filter["folder_id"] = folder_id
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter if where_filter else None,
            include=['documents', 'metadatas', 'distances']
        )
        docs = results.get('documents')
        metas = results.get('metadatas')
        dists = results.get('distances')
        if not docs or not metas or not dists or not docs[0]:
            return []

        return [
            {
                "text": doc,
                "metadata": meta,
                "score": 1 - distance
            }
            for doc, meta, distance in zip(
                docs[0],
                metas[0],
                dists[0]
            )
        ]

    async def format_context(self, search_results: List[Dict]) -> str:
        context_parts = []
        for i, result in enumerate(search_results, 1):
            filename = result['metadata']['filename']
            text = result['text']
            context_parts.append(f"[Document {i}: {filename}]\n{text}\n")
        return "\n".join(context_parts) 