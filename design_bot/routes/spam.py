from fastapi import APIRouter
from fastapi import Depends
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse

from design_bot.models.db import SpamBeforeRegistration
from .models.models import SpamPost, SpamGet
from ..methods import auth

spam = APIRouter(prefix="/sign-up", tags=["Spam"])


@spam.post("/spam", response_model=None)
async def add_user_to_spam(spam_post: SpamPost) -> PlainTextResponse:
    db.session.add(SpamBeforeRegistration(**spam_post.dict()))
    db.session.flush()
    return PlainTextResponse(status_code=201, content="User added tp spam list")


@spam.get("/spam", response_model=list[SpamGet])
async def get_spam_list(_: auth.User = Depends(auth.get_current_user)) -> list[SpamGet]:
    return parse_obj_as(list[SpamGet], db.session.query(SpamBeforeRegistration).all())
