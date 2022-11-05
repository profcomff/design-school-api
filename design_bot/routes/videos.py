from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse

from design_bot.exceptions import ObjectNotFound
from design_bot.models.db import User, Video, Direction
from .models.models import VideoPost, VideoGet
from ..methods import auth

videos = APIRouter(prefix="/video", tags=["Video"])


@videos.post("/", response_model=VideoGet)
async def add_video(video_inp: VideoPost, _: auth.User = Depends(auth.get_current_user)) -> VideoPost:
    direction: Direction = db.session.query(Direction).get(video_inp.direction_id)
    if not direction:
        raise ObjectNotFound(Direction, video_inp.direction_id)
    last_video = direction.last_video
    db.session.add(video := Video(**video_inp.dict()))
    db.session.flush()
    if last_video:
        last_video.next_video_id = video.id
        db.session.flush()
    return VideoGet.from_orm(video)


@videos.get("/{id}", response_model=VideoGet)
async def get_video(id: int) -> VideoGet:
    video = db.session.query(Video).get(id)
    if not video:
        raise ObjectNotFound(Video, id)
    return VideoGet.from_orm(video)


@videos.delete("/{id}", response_model=None)
async def delete_video(id: int, _: auth.User = Depends(auth.get_current_user)) -> None:
    video: Video = db.session.query(Video).get(id)
    if not video:
        raise ObjectNotFound(Video, id)
    video.prev_video.next_video_id = video.next_video_id
    db.session.delete(video)
    db.session.flush()
    return None


@videos.get("/", response_model=list[VideoGet])
async def get_all_videos() -> list[VideoGet]:
    return parse_obj_as(list[VideoGet], db.session.query(Video).all())

