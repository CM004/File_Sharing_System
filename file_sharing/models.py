# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    user_type = Column(String(50))  # "ops" or "client"
    is_verified = Column(Boolean, default=False)
    files = relationship("File", back_populates="uploader")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    uploader_id = Column(Integer, ForeignKey("users.id"))
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    file_type = Column(String(50))
    uploader = relationship("User", back_populates="files")

class DownloadToken(Base):
    __tablename__ = "download_tokens"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    client_user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True, index=True)
    expiry = Column(DateTime)