from fastapi import APIRouter
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse

from design_bot.exceptions import ObjectNotFound
from design_bot.models.db import User, Video, Direction
from .models.models import VideoPost, VideoGet, DirectionPost, DirectionGet

directions = APIRouter(prefix="/directions", tags=["Directions"])


@directions.post("/", response_model=DirectionPost)
async def create_direction(direction_inp: DirectionPost) -> DirectionGet:
    db.session.add(direction := Direction(**direction_inp.dict()))
    db.session.flush()
    return DirectionGet.from_orm(direction)


