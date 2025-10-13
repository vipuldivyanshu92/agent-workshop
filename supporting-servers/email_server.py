"""
Dummy Email Server
Provides inbox and outbox functionality
"""
from fastapi import APIRouter, HTTPException, status, FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum
import os

# Get base URL from environment variable or use default
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Create separate FastAPI app for Email Server with its own docs
email_app = FastAPI(
    title="Email Server API",
    description="Dummy Email Server for managing inbox and outbox",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {
            "url": f"{BASE_URL}/email",
            "description": "Email Server"
        },
        {
            "url": "http://localhost:8000/email",
            "description": "Local Development Server"
        }
    ]
)

router = APIRouter()

# In-memory storage
inbox_storage = []
outbox_storage = []
email_id_counter = {"value": 1}


class EmailStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    PENDING = "pending"
    FAILED = "failed"


class Email(BaseModel):
    id: Optional[int] = None
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    body: str
    timestamp: Optional[datetime] = None
    status: EmailStatus = EmailStatus.PENDING


class EmailCreate(BaseModel):
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    body: str


class EmailResponse(BaseModel):
    id: int
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    body: str
    timestamp: datetime
    status: EmailStatus


# Inbox Endpoints
@router.get("/inbox", response_model=List[EmailResponse])
async def get_inbox(email: Optional[str] = None):
    """
    Get all emails in inbox. Filter by recipient email if provided.
    """
    if email:
        return [e for e in inbox_storage if e["to_email"] == email]
    return inbox_storage


@router.get("/inbox/{email_id}", response_model=EmailResponse)
async def get_inbox_email(email_id: int):
    """
    Get a specific email from inbox by ID
    """
    for email in inbox_storage:
        if email["id"] == email_id:
            return email
    raise HTTPException(status_code=404, detail="Email not found")


@router.delete("/inbox/{email_id}")
async def delete_inbox_email(email_id: int):
    """
    Delete an email from inbox
    """
    global inbox_storage
    for i, email in enumerate(inbox_storage):
        if email["id"] == email_id:
            inbox_storage.pop(i)
            return {"message": "Email deleted successfully"}
    raise HTTPException(status_code=404, detail="Email not found")


# Outbox Endpoints
@router.get("/outbox", response_model=List[EmailResponse])
async def get_outbox(email: Optional[str] = None):
    """
    Get all emails in outbox. Filter by sender email if provided.
    """
    if email:
        return [e for e in outbox_storage if e["from_email"] == email]
    return outbox_storage


@router.get("/outbox/{email_id}", response_model=EmailResponse)
async def get_outbox_email(email_id: int):
    """
    Get a specific email from outbox by ID
    """
    for email in outbox_storage:
        if email["id"] == email_id:
            return email
    raise HTTPException(status_code=404, detail="Email not found")


@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def send_email(email: EmailCreate):
    """
    Send an email (adds to outbox and inbox)
    """
    email_data = {
        "id": email_id_counter["value"],
        "from_email": email.from_email,
        "to_email": email.to_email,
        "subject": email.subject,
        "body": email.body,
        "timestamp": datetime.now(),
        "status": EmailStatus.SENT
    }
    
    email_id_counter["value"] += 1
    
    # Add to outbox
    outbox_storage.append(email_data.copy())
    
    # Add to inbox with delivered status
    inbox_data = email_data.copy()
    inbox_data["status"] = EmailStatus.DELIVERED
    inbox_storage.append(inbox_data)
    
    return email_data


@router.delete("/outbox/{email_id}")
async def delete_outbox_email(email_id: int):
    """
    Delete an email from outbox
    """
    global outbox_storage
    for i, email in enumerate(outbox_storage):
        if email["id"] == email_id:
            outbox_storage.pop(i)
            return {"message": "Email deleted successfully"}
    raise HTTPException(status_code=404, detail="Email not found")


@router.post("/inbox/mark-read/{email_id}")
async def mark_email_as_read(email_id: int):
    """
    Mark an email as read (demo functionality)
    """
    for email in inbox_storage:
        if email["id"] == email_id:
            return {"message": "Email marked as read", "email_id": email_id}
    raise HTTPException(status_code=404, detail="Email not found")


@router.delete("/inbox/clear")
async def clear_inbox():
    """
    Clear all emails from inbox
    """
    global inbox_storage
    count = len(inbox_storage)
    inbox_storage = []
    return {"message": f"Cleared {count} emails from inbox"}


@router.delete("/outbox/clear")
async def clear_outbox():
    """
    Clear all emails from outbox
    """
    global outbox_storage
    count = len(outbox_storage)
    outbox_storage = []
    return {"message": f"Cleared {count} emails from outbox"}


# Include router in the email app
email_app.include_router(router)
