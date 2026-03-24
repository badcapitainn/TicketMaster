from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.ticket import Priority, Status


# ── Ticket schemas ───────────────────────────────────────────────────────────

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.medium


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    assignee_id: Optional[int] = None


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: Status
    creator_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListOut(BaseModel):
    total: int
    tickets: list[TicketOut]


# ── Comment schemas ──────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── History schemas ──────────────────────────────────────────────────────────

class HistoryOut(BaseModel):
    id: int
    ticket_id: int
    changed_by: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime

    model_config = {"from_attributes": True}
