from http.client import HTTPException

from fastapi import APIRouter, UploadFile
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse

from design_bot.exceptions import ObjectNotFound
from design_bot.models.db import User, Video, Direction, Response
from .models.models import VideoPost, VideoGet, ResponsePost, ResponseGet


response = APIRouter(prefix="/response/{user_id}", tags=["Response"])


@response.post("/file", response_model=ResponseGet)
async def upload_file(user_id: int, response_inp: ResponsePost, file: UploadFile) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != response_inp.video_id:
            raise HTTPException(403, "Forbidden")


@response.post("/video", response_model=ResponseGet)
async def upload_video(user_id: int, response_inp: ResponsePost) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != response_inp.video_id:
            raise HTTPException(403, "Forbidden")


@response.post("/text", response_model=ResponseGet)
async def upload_text(user_id: int, response_inp: ResponsePost) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != response_inp.video_id:
            raise HTTPException(403, "Forbidden")