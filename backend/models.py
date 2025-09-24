import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base

def gen_uuid():
    return str(uuid.uuid4())

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), index=True)
    role = Column(String)  # 'user' | 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")

class RecipeCache(Base):
    __tablename__ = "recipe_cache"
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String, index=True)
    title = Column(String)
    url = Column(String)
    summary = Column(Text)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("query", "url", name="uq_query_url"),)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(String, primary_key=True, default=gen_uuid)
    diet = Column(String, default="")
    allergens = Column(String, default="")  # comma-separated
    goals = Column(String, default="")      # e.g., heart-healthy, low-sodium
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
