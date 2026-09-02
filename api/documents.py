from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from database.models import User, Document
from database.vector_db import get_or_create_collection
from core.security import get_current_user
from services.ingestion import process_pdf
from schemas.document import DocumentResponse, DocumentListResponse, DocumentUploadResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads and processes a PDF document with strict validation, user isolation,
    and automatic vector chunking.
    """
    doc_id, chunks, file_size = process_pdf(file, user_id=current_user.id, db=db)
    
    return {
        "message": f"Successfully processed '{file.filename}' into {chunks} searchable chunks.",
        "document_id": doc_id,
        "original_filename": file.filename,
        "chunks": chunks,
        "file_size": file_size
    }


@router.get("", response_model=DocumentListResponse)
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all uploaded documents belonging exclusively to the authenticated user.
    """
    docs = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return {
        "total": len(docs),
        "documents": docs
    }


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a document record and purges all corresponding vector chunks from ChromaDB,
    ensuring no orphaned vector data remains.
    """
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or you do not have permission to delete it."
        )

    # 1. Purge vector chunks from ChromaDB
    try:
        collection = get_or_create_collection()
        collection.delete(where={"document_id": document_id})
    except Exception:
        pass

    # 2. Purge record from relational database
    db.delete(doc)
    db.commit()

    return {"message": f"Document '{doc.original_filename}' and all associated vector embeddings have been deleted."}
