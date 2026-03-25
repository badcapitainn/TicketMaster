from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.ticket_history import TicketHistory
from app.config import settings

engine = create_engine(settings.get_valid_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def promote_to_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email {email} not found.")
            return

        user.role = "admin"
        db.commit()
        print(f"Successfully promoted {user.username} ({email}) to admin!")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        sys.exit(1)
    
    promote_to_admin(sys.argv[1])
