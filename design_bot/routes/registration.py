from typing import Union

import sqlalchemy.exc
import starlette.status
from fastapi import APIRouter, Depends
from pydantic import parse_obj_as
from sqlalchemy import update
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from .models.models import CreateUser, SpamPost, UserGet, SpamGet, UserPatch
from fastapi_sqlalchemy import db
from design_bot.models.db import User, SpamBeforeRegistration
from design_bot.methods.google_drive import create_user_folder
import aioredis
from design_bot.settings import get_settings
from ..methods import auth

registration = APIRouter(prefix="/sign-up", tags=["Registration"])
settings = get_settings()


def redis_model_completed(model: dict[str, int | str]) -> bool:
    pass

@registration.post("/", response_model=str)
async def create_user(schema: CreateUser, _: auth.User = Depends(auth.get_current_user)) -> PlainTextResponse:
    redis_db = aioredis.from_url(settings.REDIS_DSN)
    if await redis_db.hgetall(schema.social_web_id) or db.session.query(User).filter(
            User.social_web_id == schema.social_web_id).one_or_none():
        raise HTTPException(403, "Already exists")
    await redis_db.hset(name=schema.social_web_id, key="social_web_id", value=schema.social_web_id)
    return PlainTextResponse(status_code=201, content="User created")


@registration.patch("/{social_web_id}", response_model=Union[UserGet, str])
async def add_field(social_web_id: str, schema: UserPatch,
                    _: auth.User = Depends(auth.get_current_user)) -> UserGet | PlainTextResponse:
    redis_db = aioredis.from_url(settings.REDIS_DSN)
    user: dict[str, int | str] = await redis_db.hgetall(name=social_web_id)
    if not user:
        raise HTTPException(404, "User not found")
    for k, v in schema.dict().items():
        if not v:
            continue
        await redis_db.hset(name=social_web_id, key=k, value=v)
    updated: dict[str, int | str] = await redis_db.hgetall(social_web_id)
    if updated.keys() | "" == schema.dict().keys() | "social_web_id":
        folder_id = await create_user_folder(**updated, social_web_id=social_web_id)
        try:
            db.session.add(db_user := User(**updated, folder_id=folder_id))
            db.session.flush()
        except sqlalchemy.exc.InvalidRequestError:
            return PlainTextResponse(status_code=422, content="Invalid user data")
        return UserGet.from_orm(db_user)
    return PlainTextResponse(status_code=200, content="Fields updated")


@registration.patch("/{social_web_id}", response_model=str)
async def patch_user(social_web_id: str, schema: UserPatch,
                     _: auth.User = Depends(auth.get_current_user)) -> PlainTextResponse:
    user: User = db.session.execute(
        update(User).where(User.social_web_id == social_web_id).values(**schema.dict(exclude_unset=True)))
    return PlainTextResponse(status_code=200, content="Patched")


@registration.get("/{social_web_id}", response_model=UserGet)
async def get_user(social_web_id: str, _: auth.User = Depends(auth.get_current_user)) -> UserGet:
    user: User = db.session.query(User).filter(User.social_web_id == social_web_id).one_or_none()
    if not user.first_name or not user.middle_name or not user.last_name or not user.direction_id or not user.readme or not user.union_id or not user.year:
        raise HTTPException(412, "User registration did not end")
    return UserGet.from_orm(user)
