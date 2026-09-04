import json
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from sqlalchemy.orm import Session

from core.config import settings
from database.database import init_db, get_db
from database.models import User, Conversation, Message
from core.security import get_optional_current_user
from api.auth import router as auth_router
from api.documents import router as documents_router
from api.conversations import router as conversations_router
from schemas.chat import ChatRequest, ChatResponse
from services.ingestion import process_pdf
from services.agent import run_agent
from database.vector_db import get_or_create_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQL database tables
    init_db()
    yield


app = FastAPI(title="Exam Revision Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(conversations_router)


@app.post("/api/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in to upload and manage documents."
        )
    try:
        doc_id, num_chunks, file_size = process_pdf(file, user_id=current_user.id, db=db)
        return {
            "message": f"Successfully processed {file.filename} into {num_chunks} searchable chunks!",
            "document_id": doc_id,
            "chunks": num_chunks,
            "file_size": file_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/database")
def get_database_contents(
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    try:
        collection = get_or_create_collection()
        total_items = collection.count()
        
        if total_items == 0:
            return {"total_items": 0, "data": []}
        
        # If user is authenticated, isolate results to their own chunks
        where_filter = {"user_id": current_user.id} if current_user else None
        db_data = collection.get(where=where_filter) if where_filter else collection.get()
        
        table_data = []
        ids = db_data.get('ids', [])
        metadatas = db_data.get('metadatas', [])
        documents = db_data.get('documents', [])

        for i in range(len(ids)):
            meta = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
            table_data.append({
                "id": ids[i],
                "source": meta.get('source', 'Unknown'),
                "page_number": meta.get('page_number', 1),
                "document_id": meta.get('document_id', ''),
                "content": documents[i] if i < len(documents) else ""
            })
        return {"total_items": len(table_data), "data": table_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching database: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_id = current_user.id if current_user else None
        conversation_id = request.conversation_id
        history = []
        active_conversation = None

        if user_id:
            # If conversation_id is provided, find it
            if conversation_id:
                active_conversation = (
                    db.query(Conversation)
                    .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
                    .first()
                )
            
            # If no conversation exists or invalid ID, create one
            if not active_conversation:
                # Truncate prompt for title
                auto_title = request.prompt.strip()[:40] + ("..." if len(request.prompt.strip()) > 40 else "")
                active_conversation = Conversation(
                    user_id=user_id,
                    title=auto_title or "Study Session"
                )
                db.add(active_conversation)
                db.commit()
                db.refresh(active_conversation)

            conversation_id = active_conversation.id

            # Load recent messages for conversational context
            recent_msgs = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .all()
            )
            for m in recent_msgs[-6:]:
                history.append({"role": m.role, "content": m.content})

            # Save incoming User message to PostgreSQL
            user_msg = Message(
                conversation_id=conversation_id,
                role="user",
                content=request.prompt
            )
            db.add(user_msg)
            db.commit()

        # Run the LLM tool-routing agent
        response_text, citations = run_agent(
            user_prompt=request.prompt,
            user_id=user_id,
            chat_history=history
        )

        if user_id and active_conversation:
            # Save Assistant response with JSON citations to PostgreSQL
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                sources=json.dumps(citations) if citations else None
            )
            db.add(assistant_msg)
            db.commit()

        return {
            "response": response_text,
            "conversation_id": conversation_id or "",
            "sources": citations or []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
