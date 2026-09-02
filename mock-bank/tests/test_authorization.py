from datetime import datetime

from app.models import Account, AuthorizationStatus, Base
from app.schemas.authorize import AuthorizationRequest
from app.services.authorize import (
    authorize_payment,
    encrypt_card_number,
    hash_cvv,
    normalize_card_number,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def test_normalize_and_hash_card_fields():
    assert normalize_card_number("4111 1111 1111 1111") == "4111111111111111"
    assert hash_cvv("123") != "123"
    assert encrypt_card_number("4111111111111111") != "4111111111111111"


def test_authorize_payment_success():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        account = Account(
            id="acc_123",
            customer_id="cust_123",
            card_number_encrypted=encrypt_card_number("4111111111111111"),
            card_last4="1111",
            cvv_hash=hash_cvv("123"),
            expiry_month=12,
            expiry_year=2030,
            balance_cents=1000,
            reserved_cents=0,
            label="Main card",
        )
        session.add(account)
        session.commit()

        payload = AuthorizationRequest(
            card_number="4111 1111 1111 1111",
            cvv="123",
            expiry_month=12,
            expiry_year=2030,
            amount=250,
            order_id="ord_123",
            customer_id="cust_123",
        )

        authorization = authorize_payment(session, payload)

        assert authorization.status == AuthorizationStatus.AUTHORIZED
        assert authorization.amount == 250
        assert authorization.card_last4 == "1111"
        assert account.reserved_cents == 250
        assert authorization.expires_at > datetime.utcnow()
