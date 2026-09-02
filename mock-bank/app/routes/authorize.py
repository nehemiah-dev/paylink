from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.database import get_db
    from app.schemas import authorize
    from app.services.authorize import authorize_payment_async
except ImportError:  # pragma: no cover
    from database import get_db
    from schemas import authorize
    from services.authorize import authorize_payment_async

router = APIRouter()


@router.post("/authorize", response_model=authorize.AuthorizationResponse)
async def authorization(
    payload: authorize.AuthorizationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        return await authorize_payment_async(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc