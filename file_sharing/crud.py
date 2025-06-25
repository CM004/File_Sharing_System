from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import os
from . import models, schemas
from .auth import get_password_hash

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed,
        user_type=user.user_type,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_email(db: Session, email: str):
    user = get_user_by_email(db, email)
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)
    return user

# File CRUD operations
def get_file(db: Session, file_id: int):
    return db.query(models.File).filter(models.File.id == file_id).first()

def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.File).offset(skip).limit(limit).all()

def create_file(db: Session, file: schemas.FileCreate, uploader_id: int, filename: str):
    db_file = models.File(
        filename=filename,
        uploader_id=uploader_id,
        file_type=file.file_type
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def delete_file(db: Session, file_id: int):
    file = get_file(db, file_id)
    if file:
        # Delete physical file
        file_path = os.path.join("files", file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.delete(file)
        db.commit()
    return file

# Download Token CRUD operations
def create_download_token(db: Session, file_id: int, client_user_id: int, token: str):
    # Set expiry to 1 hour from now
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    db_token = models.DownloadToken(
        file_id=file_id,
        client_user_id=client_user_id,
        token=token,
        expiry=expiry
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_download_token(db: Session, token: str):
    return db.query(models.DownloadToken).filter(
        and_(
            models.DownloadToken.token == token,
            models.DownloadToken.expiry > datetime.utcnow()
        )
    ).first()

def delete_expired_tokens(db: Session):
    """Clean up expired download tokens"""
    expired_tokens = db.query(models.DownloadToken).filter(
        models.DownloadToken.expiry <= datetime.utcnow()
    ).all()
    
    for token in expired_tokens:
        db.delete(token)
    
    db.commit()
    return len(expired_tokens)

# File validation
def is_valid_file_type(filename: str) -> bool:
    """Check if file is pptx, docx, or xlsx"""
    allowed_extensions = {'.pptx', '.docx', '.xlsx'}
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in allowed_extensions

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()
