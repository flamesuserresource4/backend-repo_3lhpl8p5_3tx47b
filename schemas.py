"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Financial advisor app schemas

class PodcastEpisode(BaseModel):
    """
    Podcast episodes collection schema
    Collection name: "podcastepisode" -> typically handled as "podcastepisode" collection
    """
    title: str
    description: Optional[str] = None
    audio_url: HttpUrl
    cover_image_url: Optional[HttpUrl] = None
    published_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)

class Inquiry(BaseModel):
    """
    Contact inquiries schema
    Collection name: "inquiry"
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    preferred_mode: Optional[str] = Field(default="online", description="online|f2f")
