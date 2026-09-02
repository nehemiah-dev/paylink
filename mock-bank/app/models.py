import uuid
from datetime import datetime
from enum import Enum as PyEnum

try:
    from app.database import Base
except ImportError:  # pragma: no cover
    from database import Base

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


def gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class AuthorizationStatus(PyEnum):
    AUTHORIZED = "authorized"
    DECLINED = "declined"
    VOIDED = "voided"
    CAPTURED = "captured"
    EXPIRED = "expired"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: gen_id("acc"))
    customer_id = Column(String, nullable=False, index=True)
    card_number_encrypted = Column(String, nullable=False, unique=True)
    card_last4 = Column(String(4), nullable=False)
    cvv_hash = Column(String, nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    balance_cents = Column(BigInteger, nullable=False, default=0)
    reserved_cents = Column(BigInteger, nullable=False, default=0)
    label = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    authorizations = relationship("Authorization", back_populates="account")

    @property
    def available_cents(self) -> int:
        return self.balance_cents - self.reserved_cents


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(String, primary_key=True, default=lambda: gen_id("auth"))
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    order_id = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    status = Column(
        Enum(AuthorizationStatus, native_enum=False),
        nullable=False,
        default=AuthorizationStatus.AUTHORIZED,
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expires_at = Column(DateTime, nullable=False)

    account = relationship("Account", back_populates="authorizations")