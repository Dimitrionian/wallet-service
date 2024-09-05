from datetime import datetime, timedelta
import typing

import fastapi
from fastapi import Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session

from app import schemas
from app.exceptions import PaymentError, UserExistsError
from app.repositories import PaymentRepository
from app.api.base import get_payment_repo, get_current_user, get_db
from app.models import User
from app.repositories.utils import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from schemas import TokenRequestForm

ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.post("/token", response_model=dict)
async def login_for_access_token(form_data: TokenRequestForm, db: Session = Depends(get_db)):
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@ROUTER.post("/user/")
async def create_user(
    data: schemas.UserCreate,
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.User:
    try:
        user = await payment_repo.create_user(payment_repo, data)
    except UserExistsError as e:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return typing.cast(schemas.User, user)


@ROUTER.get("/user/{user_id}/balance/")
async def get_user_balance(
    user_id: int,
    ts: int | None = None,
    current_user: User = Depends(get_current_user),
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.UserBalance:
    balance = await payment_repo.get_user_balance(payment_repo, user_id=user_id, ts=ts)
    if balance is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return typing.cast(schemas.UserBalance, {"amount": balance})


@ROUTER.post("/transaction/")
async def add_transaction(
    data: schemas.TransactionAdd,
    current_user: User = Depends(get_current_user),
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.Transaction:
    try:
        transaction = await payment_repo.add_transaction(payment_repo, data, await current_user)
    except PaymentError as e:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return typing.cast(schemas.Transaction, transaction)


@ROUTER.get("/transaction/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.Transaction:
    transaction = await payment_repo.get_transaction(transaction_id, payment_repo)
    if transaction is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return typing.cast(schemas.Transaction, transaction)

