from jose import jwt, JWTError

from app.infrastructure.database import settings


def decode_access_token(
    token: str,
):
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )