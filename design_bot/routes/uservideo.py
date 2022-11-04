from http.client import HTTPException

from fastapi import APIRouter
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse

from design_bot.exceptions import ObjectNotFound
from design_bot.models.db import User, Video, Direction, Response, RequestTypes
from .models.models import VideoPost, VideoGet, ResponsePost, ResponseGet



user_video = APIRouter(prefix="/uservideo", tags=["User Video"])


@user_video.get("/{user_id}", response_model=VideoGet | None)
async def get_next_video(user_id: int) -> VideoGet | PlainTextResponse:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    video = await user.next_user_video
    if video.request_type == "":
        db.session.add(Response(video_id=video.id, user_id=user.id))
        db.session.flush()
    return VideoGet.from_orm(video) if video else PlainTextResponse(status_code=200, content="Course ended")


@user_video.post("/{user_id}", response_model=ResponseGet)
async def load_homework(user_id: int, response_inp: ResponsePost) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != response_inp.video_id:
            raise HTTPException(403, "Forbidden")
    db.session.add(response := Response(**response_inp.dict()))
    db.session.flush()
    return ResponseGet.from_orm(response)