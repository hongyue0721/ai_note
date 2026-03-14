from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(
    subject: str,
    expires_minutes: int = 60 * 24,
    scope: str = "user",
    secret: str | None = None,
) -> str:
    settings = get_settings()
    expire_at = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire_at, "scope": scope}
    signing_secret = secret or settings.jwt_secret
    return jwt.encode(payload, signing_secret, algorithm=ALGORITHM)


def decode_access_token(
    token: str, secret: str | None = None
) -> dict[str, object] | None:
    settings = get_settings()
    signing_secret = secret or settings.jwt_secret
    try:
        return jwt.decode(token, signing_secret, algorithms=[ALGORITHM])
    except JWTError:
        return None
