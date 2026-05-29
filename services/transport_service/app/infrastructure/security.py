import secrets

from jose import jwt

from app.infrastructure.database import settings


def decode_access_token(
    token: str,
):
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
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
