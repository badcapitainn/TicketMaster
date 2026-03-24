import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserRole(str, enum.Enum):
    standard_user = "standard_user"
    agent = "agent"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.standard_user, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    created_tickets = relationship(
        "Ticket", foreign_keys="Ticket.creator_id", back_populates="creator"
    )
    assigned_tickets = relationship(
        "Ticket", foreign_keys="Ticket.assignee_id", back_populates="assignee"
    )
    comments = relationship("Comment", back_populates="author")
    ticket_history = relationship("TicketHistory", back_populates="changed_by_user")
