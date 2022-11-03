import starlette.status
from fastapi import APIRouter
from pydantic import parse_obj_as
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from .models.models import UserPost, SpamPost, UserGet, SpamGet
from fastapi_sqlalchemy import db
from design_bot.models.db import User, SpamBeforeRegistration
from design_bot.methods.google_drive import create_user_folder

registration = APIRouter(prefix="/sign-up", tags=["Registration"])


@registration.post("/spam", response_model=None)
async def add_user_to_spam(spam_post: SpamPost) -> PlainTextResponse:
    db.session.add(SpamBeforeRegistration(**spam_post.dict()))
    db.session.flush()
    return PlainTextResponse(status_code=201, content="User added tp spam list")


@registration.get("/spam", response_model=list[SpamGet])
async def get_spam_list() -> list[SpamGet]:
    return parse_obj_as(list[SpamGet], db.session.query(SpamBeforeRegistration).all())


@registration.post("/", response_model=UserGet)
async def sign_up(new_user: UserPost) -> UserGet:
    if db.session.query(User).filter(User.social_web_id == new_user.social_web_id).one_or_none():
        raise HTTPException(status_code=starlette.status.HTTP_409_CONFLICT, detail="Forbidden")
    folder_id = await create_user_folder(**new_user.dict())
    db.session.add(user := User(**new_user.dict(), folder_id=folder_id))
    db.session.flush()
    return UserGet.from_orm(user)



