from typing import Union

import aioredis
import sqlalchemy.exc
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from sqlalchemy import update
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse

from design_bot.methods.google_drive import create_user_folder
from design_bot.models.db import User
from design_bot.settings import get_settings
from .models.models import CreateUser, UserGet, UserPatch
from ..methods import auth

registration = APIRouter(prefix="/sign-up", tags=["Registration"])
settings = get_settings()


def redis_model_completed(model: dict[str, int | str]) -> bool:
    for row in [*UserPatch().dict().keys(), 'social_web_id']:
        if row not in model.keys():
            return False
    return True



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
    updated: dict[bytes, int | bytes] = await redis_db.hgetall(social_web_id)
    updated: dict[str, int | str] = {row.decode('utf-8'): updated[row].decode('utf-8') for row in updated.keys()}
    if redis_model_completed(updated):
        folder_id = await create_user_folder(**updated)
        try:
            db.session.add(db_user := User(**updated, folder_id=folder_id))
            db.session.flush()
        except sqlalchemy.exc.IntegrityError:
            return PlainTextResponse(status_code=422, content="Invalid user data")
        await redis_db.delete(social_web_id)
        return UserGet.from_orm(db_user)
    return PlainTextResponse(status_code=200, content="Fields updated")


@registration.patch("/{social_web_id}", response_model=UserGet)
async def patch_user(social_web_id: str, schema: UserPatch,
                     _: auth.User = Depends(auth.get_current_user)) -> UserGet:
    if not db.session.query(User).filter(User.social_web_id == social_web_id).one_or_none():
        raise HTTPException(status_code=404, detail="Not found")
    user: User = db.session.execute(
        update(User).where(User.social_web_id == social_web_id).values(**schema.dict(exclude_unset=True)))
    return UserGet.from_orm(user)


@registration.get("/{social_web_id}", response_model=UserGet)
async def get_user(social_web_id: str, _: auth.User = Depends(auth.get_current_user)) -> UserGet:
    user: User = db.session.query(User).filter(User.social_web_id == social_web_id).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return UserGet.from_orm(user)
