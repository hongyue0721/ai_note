from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)
admin_bearer_scheme = HTTPBearer(auto_error=False)


def require_user_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, object]:
    settings = get_settings()
    if credentials is None:
        raise UnauthorizedException()

    payload = decode_access_token(credentials.credentials, secret=settings.jwt_secret)
    if payload is None or payload.get("scope") != "user":
        raise UnauthorizedException("invalid token")
    return payload


def require_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_bearer_scheme),
) -> dict[str, object]:
    settings = get_settings()
    if credentials is None:
        raise UnauthorizedException()

    payload = decode_access_token(
        credentials.credentials, secret=settings.admin_jwt_secret
    )
    if payload is None or payload.get("scope") != "admin":
        raise UnauthorizedException("invalid admin token")
    return payload
