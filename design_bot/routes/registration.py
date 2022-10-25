from fastapi import APIRouter
from starlette.responses import PlainTextResponse
from .models.models import UserPost
from fastapi_sqlalchemy import db
from design_bot.models.db import User

registration = APIRouter(prefix="/sign-up", tags=["registration"])


@registration.post("/", response_model=PlainTextResponse)
async def sign_up(new_user: UserPost) -> PlainTextResponse:
    db.session.add(user := User(**new_user.dict()))
    db.session.flush()
    return PlainTextResponse(status_code=201, content="User created")

