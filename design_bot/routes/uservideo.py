from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from starlette.responses import PlainTextResponse

from design_bot.exceptions import ObjectNotFound
from design_bot.models.db import User
from .models.models import VideoGet
from ..methods import auth

user_video = APIRouter(prefix="/uservideo", tags=["User Video"])


@user_video.get("/{user_id}", response_model=VideoGet | None)
async def get_next_video(user_id: int, _: auth.User = Depends(auth.get_current_user)) -> VideoGet | PlainTextResponse:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    video = await user.next_user_video
    return VideoGet.from_orm(video) if video else PlainTextResponse(status_code=200, content="Course ended")
