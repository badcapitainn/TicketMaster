from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Optional
from app.models.ticket import Ticket, Priority, Status
from app.models.comment import Comment
from app.models.ticket_history import TicketHistory
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreate, TicketUpdate, CommentCreate


# ── Tickets ──────────────────────────────────────────────────────────────────

def create_ticket(db: Session, ticket_in: TicketCreate, creator_id: int) -> Ticket:
    db_ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        status=Status.open,
        creator_id=creator_id,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


def list_tickets(
    db: Session,
    status: Optional[Status] = None,
    priority: Optional[Priority] = None,
    assignee_id: Optional[int] = None,
    creator_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[int, list[Ticket]]:
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assignee_id is not None:
        query = query.filter(Ticket.assignee_id == assignee_id)
    if creator_id is not None:
        query = query.filter(Ticket.creator_id == creator_id)
    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return total, tickets


def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: User,
) -> Ticket:
    ticket = get_ticket(db, ticket_id)

    # Permission check
    is_creator = ticket.creator_id == current_user.id
    is_agent_or_admin = current_user.role in (UserRole.agent, UserRole.admin)

    if not (is_creator or is_agent_or_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this ticket",
        )

    # standard_users can only update title/description/status on their own tickets
    update_data = ticket_update.model_dump(exclude_unset=True)

    if current_user.role == UserRole.standard_user:
        restricted = {"priority", "assignee_id"}
        for field in restricted:
            if field in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Standard users cannot update '{field}'",
                )

    # Record changes in history
    history_entries = []
    for field, new_value in update_data.items():
        old_value = getattr(ticket, field)
        if str(old_value) != str(new_value):
            history_entries.append(
                TicketHistory(
                    ticket_id=ticket.id,
                    changed_by=current_user.id,
                    field_name=field,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                )
            )
        setattr(ticket, field, new_value)

    db.add_all(history_entries)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: int) -> dict:
    ticket = get_ticket(db, ticket_id)
    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket deleted successfully"}


# ── Comments ─────────────────────────────────────────────────────────────────

def create_comment(
    db: Session, ticket_id: int, comment_in: CommentCreate, author_id: int
) -> Comment:
    # Ensure ticket exists
    get_ticket(db, ticket_id)
    comment = Comment(ticket_id=ticket_id, author_id=author_id, body=comment_in.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments(db: Session, ticket_id: int) -> list[Comment]:
    get_ticket(db, ticket_id)
    return (
        db.query(Comment)
        .filter(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


def get_ticket_history(db: Session, ticket_id: int) -> list[TicketHistory]:
    get_ticket(db, ticket_id)
    return (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.changed_at.asc())
        .all()
    )


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_stats(db: Session) -> dict:
    total = db.query(Ticket).count()
    by_status = {
        s.value: db.query(Ticket).filter(Ticket.status == s).count()
        for s in Status
    }
    by_priority = {
        p.value: db.query(Ticket).filter(Ticket.priority == p).count()
        for p in Priority
    }
    return {
        "total_tickets": total,
        "by_status": by_status,
        "by_priority": by_priority,
    }
