import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Optional
from datetime import datetime

from database import create_document, get_documents, db

app = FastAPI(title="Financial Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ------------------------------
# Podcast Episodes Endpoints
# ------------------------------

class EpisodeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    audio_url: HttpUrl
    cover_image_url: Optional[HttpUrl] = None
    tags: List[str] = Field(default_factory=list)

class EpisodeOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    audio_url: HttpUrl
    cover_image_url: Optional[HttpUrl] = None
    tags: List[str] = Field(default_factory=list)
    published_at: datetime


def _collection_name(model_name: str) -> str:
    # Simple helper to align with schemas guidance
    return model_name.lower()


@app.get("/episodes", response_model=List[EpisodeOut])
def list_episodes(limit: Optional[int] = 50):
    docs = get_documents(_collection_name("podcastepisode"), {}, limit)
    results: List[EpisodeOut] = []
    for d in docs:
        results.append(
            EpisodeOut(
                id=str(d.get("_id")),
                title=d.get("title"),
                description=d.get("description"),
                audio_url=d.get("audio_url"),
                cover_image_url=d.get("cover_image_url"),
                tags=d.get("tags", []),
                published_at=d.get("published_at") or d.get("created_at") or datetime.utcnow(),
            )
        )
    return results


@app.post("/episodes", status_code=201)
def create_episode(payload: EpisodeCreate):
    data = payload.model_dump()
    data["published_at"] = datetime.utcnow()
    try:
        new_id = create_document(_collection_name("podcastepisode"), data)
        return {"id": new_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# Contact/Inquiries Endpoints
# ------------------------------

class InquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    preferred_mode: Optional[str] = Field(default="online", description="online|f2f")

class InquiryOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    preferred_mode: Optional[str]
    created_at: datetime


@app.post("/contact", status_code=201)
def submit_inquiry(payload: InquiryCreate):
    data = payload.model_dump()
    try:
        new_id = create_document(_collection_name("inquiry"), data)
        return {"id": new_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
