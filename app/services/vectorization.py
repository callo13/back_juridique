import ollama
import chromadb
from typing import List, Dict, Any
import numpy as np

class VectorizationService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        self.collection = self.chroma_client.get_or_create_collection("legal_documents")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = ollama.embeddings(
                model='mxbai-embed-large',
                prompt=text
            )
            embeddings.append(response['embedding'])
        return embeddings

    async def store_vectors(self, texts: List[str], metadatas: List[dict[str, str | int | float | bool | None]]) -> List[str]:
        ids = [f"doc_{meta['document_id']}_chunk_{meta['chunk_index']}" for meta in metadatas]
        embeddings = await self.create_embeddings(texts)
        embeddings_np = np.array(embeddings, dtype=np.float32)
        self.collection.add(
            documents=texts,
            metadatas=metadatas,  # type: ignore
            ids=ids,
            embeddings=embeddings_np
        )
        return ids

    async def vectorize_document(self, document_id: int, folder_id: int, filename: str, chunks: List[str]) -> bool:
        metadatas = [
            {
                "document_id": document_id,
                "folder_id": folder_id,
                "chunk_index": i,
                "filename": filename
            }
            for i, chunk in enumerate(chunks)
        ]
        await self.store_vectors(chunks, metadatas)
        return True

    def delete_vectors_by_document_id(self, document_id: int):
        # Récupère tous les ids des chunks liés à ce document
        results = self.collection.get(where={"document_id": document_id})
        ids_to_delete = results.get("ids", [])
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)