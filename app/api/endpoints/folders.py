from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import FolderCreate
from app.database.db import get_db
from app.models.database_models import Folder
from typing import List

router = APIRouter()

@router.get("/folders", response_model=List[FolderCreate])
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