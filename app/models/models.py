from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from app.db import Base
import enum

class ImageStatus(str, enum.Enum):
    pending = "pending"
    processed = "processed"
    flagged = "flagged"
    failed = "failed"

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, nullable=False)
    source_url = Column(Text, nullable=False)
    license_info = Column(String(100))
    status = Column(String(20), default=ImageStatus.pending, index=True)

class ImageMetadataRecord(Base):
    __tablename__ = "image_metadata"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True)
    subject = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    attributes = Column(ARRAY(Text))
    caption = Column(Text)
    confidence = Column(Float, nullable=False)
    model = Column(String(50))

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    subject = Column(String(100), index=True)
    category = Column(String(50))

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    similarity = Column(Float)
    verdict = Column(String(50))
    reason_code = Column(String(100))
    explanation = Column(Text)
    status = Column(String(20), default="pending")

class CostLog(Base):
    __tablename__ = "cost_log"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), index=True)
    call_type = Column(String(50))
    model = Column(String(50))
    units = Column(Integer)
    est_cost_usd = Column(Float)

# --- ADDING THE VECTOR MODELS HERE ---
class PostVector(Base):
    __tablename__ = "post_vectors"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), unique=True)
    embedding = Column(ARRAY(Float))
    model = Column(String(50))

class ImageVector(Base):
    __tablename__ = "image_vectors"
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True)
    embedding = Column(ARRAY(Float))
    model = Column(String(50))