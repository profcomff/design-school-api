from fastapi import APIRouter
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse
from .models.models import UserPost, SpamPost, VideoPost, VideoGet
from fastapi_sqlalchemy import db
from design_bot.models.db import User, SpamBeforeRegistration, Video
from design_bot.exceptions import ObjectNotFound


videos = APIRouter(prefix="/video", tags=["Video"])


@videos.post("/", response_model=VideoGet)
async def add_video(video_inp: VideoPost) -> VideoPost:
    db.session.add(video := Video(**video_inp.dict()))
    db.session.flush()
    return VideoGet.from_orm(video)


@videos.patch("/", response_model=VideoGet)
async def patch_video(video_inp: ...) -> VideoGet:
    ...


@videos.get("/{id}", response_model=VideoGet)
async def get_video(id: int) -> VideoGet:
    video = db.session.query(Video).get(id)
    if not video:
        raise ObjectNotFound(Video, id)
    return VideoGet.from_orm(video)


@videos.delete("/{id}", response_model=None)
async def delete_video(id: int) -> None:
    video = db.session.query(Video).get(id)
    if not video:
        raise ObjectNotFound(Video, id)
    db.session.delete(video)
    db.session.flush()
    return None


@videos.get("/", response_model=list[VideoGet])
async def get_all_videos() -> list[VideoGet]:
    return parse_obj_as(list[VideoGet], db.session.query(Video).all())

