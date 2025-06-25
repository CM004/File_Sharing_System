from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    user_type: str  # "ops" or "client"

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    user_type: str
    is_verified: bool
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    user_type: str
    is_verified: bool

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# File schemas
class FileBase(BaseModel):
    filename: str
    file_type: str

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: int
    uploader_id: int
    upload_time: datetime
    
    class Config:
        from_attributes = True

class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    upload_time: datetime
    uploader_username: str

# Download schemas
class DownloadRequest(BaseModel):
    file_id: int

class DownloadResponse(BaseModel):
    download_link: str
    message: str

# Email verification
class EmailVerification(BaseModel):
    token: str

# Response schemas
class MessageResponse(BaseModel):
    message: str

class FileListResponse(BaseModel):
    files: List[FileResponse]
