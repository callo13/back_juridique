from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database_models import Document, Folder
from app.models.schemas import DocumentRead, FolderRead
from app.database.db import get_db
import os
from app.config import UPLOAD_DIR
from typing import Optional
from app.services.document_processor import DocumentProcessor
from app.services.vectorization import VectorizationService
from datetime import datetime
from fastapi.responses import JSONResponse

router = APIRouter()

document_processor = DocumentProcessor()
vectorization_service = VectorizationService()

@router.post("/vectorize")
async def vectorize_document(
    file: UploadFile = File(...),
    folder_name: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Valider le fichier (type, taille)
    filename = file.filename or "uploaded_file"
    if not filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Type de fichier non supporté")

    upload_dir = str(UPLOAD_DIR) if UPLOAD_DIR is not None else "./uploads"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 2. Chercher ou créer le dossier
    folder = db.query(Folder).filter(Folder.name == folder_name).first()
    if not folder:
        folder = Folder(name=folder_name)
        db.add(folder)
        db.commit()
        db.refresh(folder)

    # Vérifier si le document existe déjà dans le dossier
    existing_doc = db.query(Document).filter(Document.folder_id == folder.id, Document.filename == file.filename).first()
    if existing_doc:
        raise HTTPException(status_code=400, detail="Un document avec ce nom existe déjà dans ce dossier.")

    # 3. Créer l'entrée en BDD
    document = Document(
        folder_id=folder.id,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        processing_status="processing"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # 4. Traitement et vectorisation
    try:
        file_type = file.content_type if file.content_type is not None else 'unknown'
        chunks = await document_processor.process_document(file_path, file_type)
        await vectorization_service.vectorize_document(getattr(document, 'id'), getattr(folder, 'id'), filename, chunks)
        setattr(document, 'processing_status', 'completed')
        setattr(document, 'chunk_count', len(chunks))
        setattr(document, 'processed_at', datetime.utcnow())
    except Exception as e:
        setattr(document, 'processing_status', 'failed')
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vectorisation : {str(e)}")

    db.commit()
    db.refresh(document)

    return DocumentRead.from_orm(document) 