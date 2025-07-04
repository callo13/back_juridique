from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.services.vectorization import VectorizationService
from sqlalchemy import event

Base = declarative_base()

class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    processing_status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime)
    folder = relationship("Folder", back_populates="documents")

# Hook pour supprimer les vecteurs ChromaDB lors de la suppression d'un document
@event.listens_for(Document, "after_delete")
def delete_document_vectors(mapper, connection, target):
    try:
        doc_id = getattr(target, 'id', None)
        if doc_id is not None:
            vector_service = VectorizationService()
            vector_service.delete_vectors_by_document_id(int(doc_id))
    except Exception:
        pass 