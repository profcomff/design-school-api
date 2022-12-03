import random
import string

import starlette.status
from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from sqlalchemy import update
from fastapi import HTTPException

from design_bot.models.db import User, Direction
from .models.models import UserPost, UserGet, UserPatch
from ..methods import auth
from ..methods.google_drive import create_user_folder, drive

registration = APIRouter(prefix="/user", tags=["Registration"])


@registration.post("/", response_model=UserGet)
async def sign_up(new_user: UserPost, _: auth.User = Depends(auth.get_current_user)) -> UserGet:
    if db.session.query(User).filter(User.social_web_id == new_user.social_web_id).one_or_none():
        raise HTTPException(status_code=starlette.status.HTTP_409_CONFLICT, detail="Forbidden")
    if not db.session.query(Direction).get(new_user.direction_id):
        raise HTTPException(status_code=404, detail="Dirrection doesnt exists")
    folder_id = await create_user_folder(**new_user.dict())
    if len(new_user.readme):
        random_string = ''.join(random.choice(string.ascii_letters) for _ in range(12))
        file = drive.CreateFile(
            {
                'title': f'{new_user.first_name}_{new_user.middle_name}_{new_user.last_name}_{new_user.social_web_id}_README_{random_string}.txt',
                "parents": [{"id": folder_id}],
            }
        )
        file.SetContentString(new_user.readme)
        file.Upload()
    db.session.add(user := User(**new_user.dict(), folder_id=folder_id))
    db.session.flush()
    return UserGet.from_orm(user)


@registration.patch("/{social_web_id}", response_model=UserGet)
async def patch_user(social_web_id: str, schema: UserPatch, _: auth.User = Depends(auth.get_current_user)) -> UserGet:
    user_query = db.session.query(User.social_web_id == social_web_id)
    if not user_query.all():
        raise HTTPException(status_code=404, detail="User not found")
    user_query.update(**schema.dict(exclude_unset=True))
    db.session.flush()
    return UserGet.from_orm(user_query.one())


@registration.get("/{social_web_id}", response_model=UserGet)
async def get_user(social_web_id: str, _: auth.User = Depends(auth.get_current_user)) -> UserGet:
    user: User = db.session.query(User).filter(User.social_web_id == social_web_id).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserGet.from_orm(user)


@registration.get("/", response_model=list[UserGet])
async def get_users(_: auth.User = Depends(auth.get_current_user)) -> list[UserGet]:
    users = db.session.query(User).all()
    if not users:
        raise HTTPException(status_code=404)
    return parse_obj_as(list[UserGet], db.session.query(User).all())
