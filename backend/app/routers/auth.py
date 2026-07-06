from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.auth.jwt import get_password_hash, verify_password, create_access_token, get_current_user, require_role
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.employee_id == user.employee_id) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID or email already exists")

    db_user = User(
        employee_id=user.employee_id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        branch=user.branch,
        region=user.region,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_id == req.employee_id).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(
        access_token=token,
        user=UserResponse.from_orm(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    return db.query(User).filter(User.is_active == True).all()


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": "User deactivated"}
