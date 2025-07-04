from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import FolderCreate, DocumentRead, FolderRead, DocumentCreate
from app.database.db import get_db
from app.models.database_models import Folder, Document
from typing import List
import os
from sqlalchemy import event

router = APIRouter()

@router.get("/folders", response_model=List[FolderRead])
async def list_folders(db: Session = Depends(get_db)):
    """Liste tous les dossiers"""
    return db.query(Folder).all()

@router.post("/folders", response_model=FolderCreate)
async def create_folder(folder: FolderCreate, db: Session = Depends(get_db)):
    """Crée un nouveau dossier"""
    db_folder = Folder(name=folder.name)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    """Supprime un dossier et ses documents"""
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    db.delete(folder)
    db.commit()
    return {"ok": True}

@router.get("/folders/{folder_id}/documents", response_model=List[DocumentRead])
async def get_documents_by_folder(folder_id: int, db: Session = Depends(get_db)):
    """Récupère tous les documents d'un dossier donné."""
    documents = db.query(Document).filter(Document.folder_id == folder_id).all()
    return documents

@router.get("/documents", response_model=List[DocumentRead])
async def list_documents(db: Session = Depends(get_db)):
    """Liste tous les documents."""
    return db.query(Document).all()

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Supprime un document par son id."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    # Supprimer le fichier physique si présent
    file_path = getattr(document, 'file_path', None)
    if file_path and isinstance(file_path, str) and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
    db.delete(document)
    db.commit()
    return {"ok": True}

@router.get("/folders/{folder_id}", response_model=FolderRead)
async def get_folder(folder_id: int, db: Session = Depends(get_db)):
    """Récupère un dossier par son id."""
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.put("/folders/{folder_id}", response_model=FolderRead)
async def update_folder(folder_id: int, folder_update: FolderCreate, db: Session = Depends(get_db)):
    """Met à jour un dossier."""
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    setattr(folder, 'name', folder_update.name)
    db.commit()
    db.refresh(folder)
    return folder

@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Récupère un document par son id."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/documents/{document_id}", response_model=DocumentRead)
async def update_document(document_id: int, document_update: DocumentCreate, db: Session = Depends(get_db)):
    """Met à jour un document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)
    return document

@event.listens_for(Document, "after_delete")
def delete_document_file(mapper, connection, target):
    file_path = getattr(target, 'file_path', None)
    if file_path and isinstance(file_path, str) and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass 