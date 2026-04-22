import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.vector_db import get_or_create_collection

def process_pdf(uploaded_file):
    """Extracts text from a Streamlit UploadedFile, chunks it, and stores it."""
    
    # 1. Extract Text
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    raw_text = ""
    for page in pdf_reader.pages:
        raw_text += page.extract_text() + "\n"

    # 2. Chunk the Text
    # We split it so the AI doesn't get overwhelmed reading 100 pages at once
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, # Overlap keeps context between paragraphs
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)

    # 3. Store in Vector DB
    collection = get_or_create_collection()

    # Generate unique IDs for each chunk (e.g., doc_name_chunk_1)
    ids = [f"{uploaded_file.name}_chunk_{i}" for i in range(len(chunks))]
    
    # Add to ChromaDB (Chroma handles the embedding automatically by default)
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=[{"source": uploaded_file.name} for _ in chunks]
    )
    
    return len(chunks)