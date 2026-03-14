from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_token, require_user_token
from app.core.config import get_settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.user import User
from app.schemas.auth import (
    AdminLoginData,
    AdminLoginRequest,
    AdminProfile,
    UserLoginData,
    UserLoginRequest,
    UserProfile,
    UserRegisterRequest,
)
from app.schemas.common import ApiResponse


router = APIRouter(tags=["auth"])


def _build_user_profile(user: User) -> UserProfile:
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        status=user.status,
    )


def _build_admin_profile(admin: AdminUser) -> AdminProfile:
    return AdminProfile(
        id=admin.id,
        username=admin.username,
        display_name=admin.display_name,
        status=admin.status,
    )


@router.post("/auth/register")
def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[UserProfile]:
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing is not None:
        raise ConflictException("username already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(data=_build_user_profile(user))


@router.post("/auth/login")
def login_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[UserLoginData]:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedException("invalid username or password")

    token = create_access_token(subject=str(user.id), scope="user")
    return ApiResponse(
        data=UserLoginData(
            access_token=token,
            user=_build_user_profile(user),
        )
    )


@router.get("/me")
def get_me(
    token_payload: dict[str, object] = Depends(require_user_token),
    db: Session = Depends(get_db),
) -> ApiResponse[UserProfile]:
    user_id = token_payload.get("sub")
    user = db.get(User, UUID(str(user_id)))
    if user is None:
        raise UnauthorizedException("user not found")
    return ApiResponse(data=_build_user_profile(user))


@router.post("/admin/auth/login")
def login_admin(
    payload: AdminLoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AdminLoginData]:
    admin = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise UnauthorizedException("invalid admin username or password")

    settings = get_settings()
    token = create_access_token(
        subject=str(admin.id),
        scope="admin",
        secret=settings.admin_jwt_secret,
    )
    return ApiResponse(
        data=AdminLoginData(
            access_token=token,
            admin=_build_admin_profile(admin),
        )
    )


@router.get("/admin/me")
def get_admin_me(
    token_payload: dict[str, object] = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> ApiResponse[AdminProfile]:
    admin_id = token_payload.get("sub")
    admin = db.get(AdminUser, UUID(str(admin_id)))
    if admin is None:
        raise UnauthorizedException("admin not found")
    return ApiResponse(data=_build_admin_profile(admin))
