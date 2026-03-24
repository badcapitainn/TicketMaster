from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.models.ticket import Priority, Status
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketOut, TicketListOut,
    CommentCreate, CommentOut, HistoryOut,
)
from app.core.dependencies import get_current_user, require_admin
from app.crud import ticket as ticket_crud

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new ticket. Status is automatically set to 'Open'."""
    return ticket_crud.create_ticket(db, ticket_in, creator_id=current_user.id)


@router.get("", response_model=TicketListOut)
def list_tickets(
    status: Optional[Status] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee"),
    creator_id: Optional[int] = Query(None, description="Filter by creator"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tickets with optional filters. Supports pagination via skip/limit."""
    total, tickets = ticket_crud.list_tickets(
        db, status=status, priority=priority,
        assignee_id=assignee_id, creator_id=creator_id,
        skip=skip, limit=limit,
    )
    return TicketListOut(total=total, tickets=tickets)


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single ticket by ID."""
    return ticket_crud.get_ticket(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a ticket. Permission rules:
    - **standard_user**: can only update their own ticket's title/description/status
    - **agent**: can update any ticket including priority and assignee
    - **admin**: full access
    """
    return ticket_crud.update_ticket(db, ticket_id, ticket_update, current_user)


@router.delete("/{ticket_id}", dependencies=[Depends(require_admin)])
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """Delete a ticket. **Admin only.**"""
    return ticket_crud.delete_ticket(db, ticket_id)


# ── Comments ──────────────────────────────────────────────────────────────────

@router.post("/{ticket_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(
    ticket_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a ticket."""
    return ticket_crud.create_comment(db, ticket_id, comment_in, author_id=current_user.id)


@router.get("/{ticket_id}/comments", response_model=list[CommentOut])
def list_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all comments on a ticket."""
    return ticket_crud.get_comments(db, ticket_id)


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/{ticket_id}/history", response_model=list[HistoryOut])
def ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the full audit history of changes made to a ticket."""
    return ticket_crud.get_ticket_history(db, ticket_id)
