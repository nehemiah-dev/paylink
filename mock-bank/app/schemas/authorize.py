from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator

try:
    from app.models import AuthorizationStatus
except ImportError:  # pragma: no cover
    from models import AuthorizationStatus


class AuthorizationRequest(BaseModel):
    card_number: str
    cvv: str
    expiry_month: int = Field(ge=1, le=12)
    expiry_year: int = Field(ge=datetime.now(UTC).year)
    amount: int = Field(gt=0, description="Amount in cents")
    order_id: str
    customer_id: str

    @field_validator("card_number")
    @classmethod
    def strip_card(cls, v: str) -> str:
        value = v.replace(" ", "").replace("-", "").strip()
        if len(value) < 12 or len(value) > 19 or not value.isdigit():
            raise ValueError("card_number must be a valid numeric card number")
        return value

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        value = v.strip()
        if not value.isdigit() or len(value) not in {3, 4}:
            raise ValueError("cvv must be a 3 or 4 digit numeric value")
        return value


class AuthorizationResponse(BaseModel):
    id: str
    authorization_id: str
    status: AuthorizationStatus
    amount: int
    order_id: str
    customer_id: str
    card_last4: str
    created_at: datetime
    expires_at: datetime