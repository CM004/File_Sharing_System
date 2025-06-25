from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import timedelta
from . import crud, models, schemas, auth, email
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
os.makedirs("files", exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/ops/login", response_model=schemas.Token)

def ops_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    u = auth.authenticate_user(db, user.username, user.password)
    if not u:
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    if u.user_type != "ops":
        raise HTTPException(status_code=403, detail="Only Ops users can login here")
    token = auth.create_access_token({"sub": u.username}, timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.post("/ops/upload", response_model=schemas.File)
def upload_file(file: UploadFile = File(...), user: models.User = Depends(auth.get_current_ops_user), db: Session = Depends(get_db)):
    if not crud.is_valid_file_type(file.filename):
        raise HTTPException(status_code=400, detail="Only pptx, docx, and xlsx files are allowed")
    path = os.path.join("files", file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    file_data = schemas.FileCreate(filename=file.filename, file_type=crud.get_file_extension(file.filename))
    db_file = crud.create_file(db, file_data, user.id, file.filename)
    return db_file

@app.post("/client/signup", response_model=schemas.MessageResponse)
def client_signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.user_type != "client":
        raise HTTPException(status_code=400, detail="Only client users can sign up through this endpoint")
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.create_user(db, user)
    token = email.generate_verification_token()
    email.store_verification_token(user.email, token)
    email.send_verification_email(user.email, token)
    return {"message": "User created successfully. Please check your email for verification."}

@app.get("/client/verify", response_model=schemas.MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    mail = email.get_verification_token(token)
    if not mail:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    u = crud.verify_user_email(db, mail)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Email verified successfully"}

@app.post("/client/login", response_model=schemas.Token)
def client_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    u = auth.authenticate_user(db, user.username, user.password)
    if not u:
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    if u.user_type != "client":
        raise HTTPException(status_code=403, detail="Only Client users can login here")
    if not u.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
    token = auth.create_access_token({"sub": u.username}, timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.get("/client/files", response_model=List[schemas.FileResponse])
def list_files(user: models.User = Depends(auth.get_current_client_user), db: Session = Depends(get_db)):
    files = crud.get_files(db)
    out = []
    for f in files:
        uploader = crud.get_user(db, f.uploader_id)
        out.append(schemas.FileResponse(id=f.id, filename=f.filename, file_type=f.file_type, upload_time=f.upload_time, uploader_username=uploader.username if uploader else "Unknown"))
    return out

@app.post("/client/download/{file_id}", response_model=schemas.DownloadResponse)
def request_download(file_id: int, user: models.User = Depends(auth.get_current_client_user), db: Session = Depends(get_db)):
    f = crud.get_file(db, file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    token = auth.generate_secure_token()
    crud.create_download_token(db, file_id, user.id, token)
    link = f"/client/download-file/{token}"
    return {"download_link": link, "message": "success"}
@app.get("/client/download-file/{token}")

def download_file(token: str, user: models.User = Depends(auth.get_current_client_user), db: Session = Depends(get_db)):
    t = crud.get_download_token(db, token)
    if not t:
        raise HTTPException(status_code=400, detail="Invalid or expired download token")
    if t.client_user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    f = crud.get_file(db, t.file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    path = os.path.join("files", f.filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on server")
    db.delete(t)
    db.commit()
    return FileResponse(path=path, filename=f.filename, media_type='application/octet-stream')
@app.get("/")

def read_root():
    return {"message": "Secure File Sharing System API"}
@app.get("/health")

def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
