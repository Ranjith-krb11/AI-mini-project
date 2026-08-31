from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from contextlib import asynccontextmanager
from core.config import settings
from database.database import init_db
from api.auth import router as auth_router
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

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        num_chunks = process_pdf(file)
        return {"message": f"Successfully processed {file.filename} into {num_chunks} searchable chunks!", "chunks": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/database")
def get_database_contents():
    try:
        collection = get_or_create_collection()
        total_items = collection.count()
        
        if total_items == 0:
            return {"total_items": 0, "data": []}
        
        db_data = collection.get()
        table_data = []
        for i in range(len(db_data['ids'])):
            table_data.append({
                "id": db_data['ids'][i],
                "source": db_data['metadatas'][i].get('source', 'Unknown'),
                "content": db_data['documents'][i]
            })
        return {"total_items": total_items, "data": table_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching database: {str(e)}")

@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        response = run_agent(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
