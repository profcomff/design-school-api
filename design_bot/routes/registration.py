from fastapi import APIRouter
from starlette.responses import PlainTextResponse
from .models.models import UserPost, SpamPost, UserGet
from fastapi_sqlalchemy import db
from design_bot.models.db import User, SpamBeforeRegistration

registration = APIRouter(prefix="/sign-up", tags=["Registration"])


@registration.post("/spam", response_model=None)
async def add_user_to_spam(spam_post: SpamPost) -> PlainTextResponse:
    db.session.add(SpamBeforeRegistration(**spam_post.dict()))
    db.session.flush()
    return PlainTextResponse(status_code=201, content="User added tp spam list")


@registration.post("/", response_model=UserGet)
async def sign_up(new_user: UserPost) -> PlainTextResponse:
    db.session.add(user := User(**new_user.dict()))
    db.session.flush()
    return UserGet.from_orm(user)



