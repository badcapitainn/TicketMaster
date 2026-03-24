import enum
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum as SAEnum,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Priority(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class Status(str, enum.Enum):
    open = "Open"
    pending = "Pending"
    resolved = "Resolved"
    closed = "Closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SAEnum(Priority), default=Priority.medium, nullable=False)
    status = Column(SAEnum(Status), default=Status.open, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tickets")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tickets")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")
