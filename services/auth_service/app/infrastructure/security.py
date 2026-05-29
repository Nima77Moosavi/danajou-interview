import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.infrastructure.database import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: str,
    role: str,
    gender: str,
    phone_number: str,
) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "role": role,
        "gender": gender,
        "phone_number": phone_number,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def _configured_service_credentials() -> dict[str, str]:
    credentials: dict[str, str] = {}

    for item in settings.SERVICE_CREDENTIALS.split(","):
        if not item.strip() or ":" not in item:
            continue

        username, password = item.split(":", 1)
        credentials[username.strip()] = password.strip()

    return credentials


def validate_service_credentials(username: str, password: str) -> bool:
    expected_password = _configured_service_credentials().get(username)

    if expected_password is None:
        return False

    return secrets.compare_digest(password, expected_password)
