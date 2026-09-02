import io
import uuid
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from database.vector_db import get_or_create_collection
from database.models import Document

# Maximum allowable file size (15 MB)
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024


def validate_pdf_upload(uploaded_file: UploadFile, contents: bytes) -> None:
    """
    Validates uploaded file against security and formatting constraints:
    - Filename extension (.pdf)
    - MIME content-type
    - Empty file (0 bytes)
    - Maximum file size (15 MB)
    """
    # 1. Filename validation
    if not uploaded_file.filename or not uploaded_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files (.pdf) are supported."
        )

    # 2. MIME type validation
    if uploaded_file.content_type and uploaded_file.content_type not in [
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{uploaded_file.content_type}'. Expected 'application/pdf'."
        )

    # 3. Empty file check
    file_size = len(contents)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes). Please upload a valid document."
        )

    # 4. Maximum size check
    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {max_mb}MB."
        )


def process_pdf(
    uploaded_file: UploadFile,
    user_id: int,
    db: Session
) -> Tuple[str, int, int]:
    """
    Validates, extracts, chunks, and indexes a PDF document:
    - Validates file integrity and size
    - Extracts text page-by-page to retain accurate page citations
    - Persists document record in PostgreSQL with status
    - Stores vector chunks in ChromaDB with user_id and document_id metadata
    
    Returns: (document_id, total_chunks, file_size)
    """
    try:
        contents = uploaded_file.file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}"
        )

    # 1. Validation
    validate_pdf_upload(uploaded_file, contents)
    file_size = len(contents)

    # 2. PDF Parsing & Integrity Check
    try:
        pdf_stream = io.BytesIO(contents)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        
        if pdf_reader.is_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Encrypted or password-protected PDFs are not supported."
            )
            
        total_pages = len(pdf_reader.pages)
        if total_pages == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF contains no pages."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrupted or unreadable PDF document: {str(e)}"
        )

    # 3. Page-by-page text extraction
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    all_chunks = []
    chunk_metadatas = []
    total_extracted_characters = 0

    document_id = str(uuid.uuid4())
    original_filename = uploaded_file.filename

    for page_idx, page in enumerate(pdf_reader.pages, start=1):
        page_text = page.extract_text() or ""
        total_extracted_characters += len(page_text.strip())

        if not page_text.strip():
            continue

        page_chunks = text_splitter.split_text(page_text)
        for chunk in page_chunks:
            chunk_number = len(all_chunks)
            all_chunks.append(chunk)
            chunk_metadatas.append({
                "document_id": document_id,
                "user_id": user_id,
                "source": original_filename,
                "page_number": page_idx,
                "chunk_number": chunk_number
            })

    # 4. Text Extraction Failure Check
    if total_extracted_characters == 0 or len(all_chunks) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract readable text from this PDF. It may contain scanned image-only pages or be empty."
        )

    # 5. Save Document record to relational database (PostgreSQL / SQLite)
    doc_record = Document(
        id=document_id,
        user_id=user_id,
        original_filename=original_filename,
        file_size=file_size,
        status="ready",
        chunk_count=len(all_chunks)
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # 6. Store in ChromaDB with document_id chunk prefixes
    collection = get_or_create_collection()
    chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(all_chunks))]

    collection.add(
        documents=all_chunks,
        ids=chunk_ids,
        metadatas=chunk_metadatas
    )

    return document_id, len(all_chunks), file_size
