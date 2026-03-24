from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, RoleUpdate
from app.core.dependencies import get_current_user, require_admin
from app.crud import user as user_crud

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_admin)])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all users. **Admin only.**"""
    return user_crud.get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID. **Admin only.**"""
    return user_crud.get_user_by_id(db, user_id)


@router.patch("/{user_id}/role", response_model=UserOut, dependencies=[Depends(require_admin)])
def change_role(
    user_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
):
    """Change a user's role. **Admin only.**"""
    return user_crud.update_user_role(db, user_id, role_update.role)


@router.patch("/{user_id}/deactivate", response_model=UserOut, dependencies=[Depends(require_admin)])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Deactivate a user account. **Admin only.**"""
    return user_crud.deactivate_user(db, user_id)
