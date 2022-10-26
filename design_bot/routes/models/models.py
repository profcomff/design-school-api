from .base import BaseModel
from design_bot.models.db import Year, RequestTypes, Directions
from pydantic import HttpUrl


class UserPost(BaseModel):
    union_id: int
    direction_id: int
    first_name: str
    middle_name: str
    last_name: str
    year: Year
    readme: str
    link: HttpUrl


class UserGet(UserPost):
    id: int


class SpamPost(BaseModel):
    user_link: HttpUrl


class VideoPost(BaseModel):
    link: HttpUrl
    request: str | None
    direction_id: int
    request_type: RequestTypes


class VideoGet(VideoPost):
    id: int


class ResponsePost(BaseModel):
    content: str | None
    video_id: int
    user_id: int


class ResponseGet(ResponsePost):
    id: int


class DirectionPost(BaseModel):
    link: HttpUrl
    name: Directions


class DirectionGet(DirectionPost):
    id: int


