# Secure File Sharing System

This is a simple file sharing system built with FastAPI and MySQL. There are two types of users: Ops and Client. Ops can upload files, and Clients can sign up, verify email, login, list files, and download files securely.

## Features
- Ops user can login and upload .pptx, .docx, .xlsx files
- Client user can sign up, verify email, login, list files, and download files
- Secure download links for files
- JWT authentication for protected routes

## Setup

### 1. Clone the repo and install requirements
```bash
cd /path/to/project
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up MySQL database
- Start MySQL (e.g., with XAMPP)
- Create a database called `file_sharing`

### 3. Run the app
```bash
uvicorn file_sharing.main:app --reload
```
- The app will create tables automatically.

### 4. Create an Ops user
- Open a Python shell:
```bash
python
```
- Run:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("ops123"))
```
- Copy the hash and insert an Ops user in MySQL:
```sql
INSERT INTO users (username, email, password_hash, user_type, is_verified) VALUES ('ops1', 'ops1@example.com', '<your_hash>', 'ops', 1);
```

### 5. Open the API docs
Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Running Tests
```bash
pytest file_sharing/tests/
```

## Endpoints
- `/ops/login` - Ops user login
- `/ops/upload` - Upload file (Ops only)
- `/client/signup` - Client sign up
- `/client/verify` - Email verification
- `/client/login` - Client login
- `/client/files` - List files (Client only)
- `/client/download/{file_id}` - Get download link (Client only)
- `/client/download-file/{token}` - Download file (Client only)
- `/` - API root
- `/health` - Health check

## Notes
- Only .pptx, .docx, .xlsx files can be uploaded
- Only verified clients can login and download files
- All protected endpoints require JWT token (Authorize in Swagger UI)
- No extra files or endpoints are included, only what the assignment asks
