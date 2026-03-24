from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(String(500), nullable=True)
    new_value = Column(String(500), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="history")
    changed_by_user = relationship("User", back_populates="ticket_history")
