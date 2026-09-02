import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

try:
    from app.models import Account, Authorization, AuthorizationStatus
    from app.schemas.authorize import AuthorizationRequest, AuthorizationResponse
except ImportError:  # pragma: no cover
    from models import Account, Authorization, AuthorizationStatus
    from schemas.authorize import AuthorizationRequest, AuthorizationResponse

SECRET_KEY = "paylink-mock-bank-demo-key"


def normalize_card_number(card_number: str) -> str:
    return card_number.replace(" ", "").replace("-", "").strip()


def encrypt_card_number(card_number: str) -> str:
    normalized = normalize_card_number(card_number)
    payload = f"{SECRET_KEY}:{normalized}".encode()
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decrypt_card_number(value: str) -> str:
    decoded = base64.urlsafe_b64decode(value.encode("utf-8")).decode("utf-8")
    return decoded.split(":", 1)[1]


def hash_cvv(cvv: str) -> str:
    return hmac.new(SECRET_KEY.encode("utf-8"), cvv.strip().encode("utf-8"), hashlib.sha256).hexdigest()


def authorize_payment(session, payload: AuthorizationRequest) -> AuthorizationResponse:
    normalized_card = normalize_card_number(payload.card_number)
    result = session.execute(select(Account).where(Account.customer_id == payload.customer_id))
    accounts = result.scalars().all()

    account = None
    for candidate in accounts:
        if decrypt_card_number(candidate.card_number_encrypted) == normalized_card:
            account = candidate
            break

    if account is None:
        raise ValueError("Card not found for customer")

    if account.expiry_month != payload.expiry_month or account.expiry_year != payload.expiry_year:
        raise ValueError("Card expiry does not match")

    if account.expiry_year < datetime.now(UTC).year or (
        account.expiry_year == datetime.now(UTC).year and account.expiry_month < datetime.now(UTC).month
    ):
        raise ValueError("Card is expired")

    if account.cvv_hash != hash_cvv(payload.cvv):
        raise ValueError("Invalid CVV")

    if payload.amount > account.available_cents:
        raise ValueError("Insufficient funds")

    account.reserved_cents += payload.amount
    authorization = Authorization(
        account_id=account.id,
        amount_cents=payload.amount,
        order_id=payload.order_id,
        customer_id=payload.customer_id,
        status=AuthorizationStatus.AUTHORIZED,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    session.add(authorization)
    session.commit()
    session.refresh(authorization)

    return AuthorizationResponse(
        id=authorization.id,
        authorization_id=authorization.id,
        status=authorization.status,
        amount=authorization.amount_cents,
        order_id=authorization.order_id,
        customer_id=authorization.customer_id,
        card_last4=account.card_last4,
        created_at=authorization.created_at,
        expires_at=authorization.expires_at,
    )


async def authorize_payment_async(session, payload: AuthorizationRequest) -> AuthorizationResponse:
    normalized_card = normalize_card_number(payload.card_number)
    result = await session.execute(select(Account).where(Account.customer_id == payload.customer_id))
    accounts = result.scalars().all()

    account = None
    for candidate in accounts:
        if decrypt_card_number(candidate.card_number_encrypted) == normalized_card:
            account = candidate
            break

    if account is None:
        raise ValueError("Card not found for customer")

    if account.expiry_month != payload.expiry_month or account.expiry_year != payload.expiry_year:
        raise ValueError("Card expiry does not match")

    if account.expiry_year < datetime.now(UTC).year or (
        account.expiry_year == datetime.now(UTC).year and account.expiry_month < datetime.now(UTC).month
    ):
        raise ValueError("Card is expired")

    if account.cvv_hash != hash_cvv(payload.cvv):
        raise ValueError("Invalid CVV")

    if payload.amount > account.available_cents:
        raise ValueError("Insufficient funds")

    account.reserved_cents += payload.amount
    authorization = Authorization(
        account_id=account.id,
        amount_cents=payload.amount,
        order_id=payload.order_id,
        customer_id=payload.customer_id,
        status=AuthorizationStatus.AUTHORIZED,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    session.add(authorization)
    await session.commit()
    await session.refresh(authorization)

    return AuthorizationResponse(
        id=authorization.id,
        authorization_id=authorization.id,
        status=authorization.status,
        amount=authorization.amount_cents,
        order_id=authorization.order_id,
        customer_id=authorization.customer_id,
        card_last4=account.card_last4,
        created_at=authorization.created_at,
        expires_at=authorization.expires_at,
    )