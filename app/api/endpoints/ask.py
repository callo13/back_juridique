from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import FolderRead
from app.database.db import get_db
from app.services.retrieval import RetrievalService
from app.services.llm_service import LLMService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    folder_id: Optional[int] = None

@router.post("/ask")
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    retrieval_service = RetrievalService()
    llm_service = LLMService()
    # 1. Recherche sémantique
    search_results = await retrieval_service.search_similar(request.question, folder_id=request.folder_id)
    if not search_results:
        return {"answer": "Aucun contexte pertinent trouvé dans les documents."}
    context = await retrieval_service.format_context(search_results)
    # 2. Génération de la réponse
    answer = await llm_service.generate_answer(request.question, context)
    return {"answer": answer, "sources": [r['metadata']['filename'] for r in search_results]} 