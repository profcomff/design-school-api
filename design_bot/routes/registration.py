import starlette.status
from fastapi import APIRouter
from pydantic import parse_obj_as
from sqlalchemy import update
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from .models.models import UserPost, SpamPost, UserGet, SpamGet, UserPatch, UserGetWithFolder
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
    db.session.add(user := User(**new_user.dict(), folder_id=None))
    db.session.flush()
    return UserGet.from_orm(user)


@registration.post("/{social_web_id}", response_model=UserGetWithFolder)
async def create_folder(social_web_id: str) -> UserGetWithFolder:
    user: User = db.session.query(User).filter(User.social_web_id == social_web_id).one_or_none()
    if not user.first_name or not user.middle_name or not user.last_name or not user.direction_id or not user.readme or not user.union_id or not user.year:
        raise HTTPException(412, "User registration did not end")
    if user.folder_id:
        raise HTTPException(403, "Already exists")
    folder_id = await create_user_folder(**UserGet.from_orm(user).dict())
    user.folder_id = folder_id
    db.session.flush()
    return UserGetWithFolder.from_orm(user)


@registration.patch("/{social_web_id}", response_model=str)
async def patch_user(social_web_id: str, schema: UserPatch) -> PlainTextResponse:
    user: User = db.session.execute(update(User).where(User.social_web_id == social_web_id).values(**schema.dict(exclude_unset=True)))
    return PlainTextResponse(status_code=200, content="Patched")


@registration.get("/{social_web_id}", response_model=UserGet)
async def get_user(social_web_id: str) -> UserGet:
    user: User = db.session.query(User).filter(User.social_web_id == social_web_id).one_or_none()
    if not user.first_name or not user.middle_name or not user.last_name or not user.direction_id or not user.readme or not user.union_id or not user.year:
        raise HTTPException(412, "User registration did not end")
    return UserGet.from_orm(user)
