from .base import Base
from design_bot.models.db import Year, RequestTypes, Directions
from pydantic import HttpUrl


class UserPost(Base):
    union_id: int
    direction_id: int
    first_name: str
    middle_name: str
    last_name: str
    year: Year
    readme: str
    social_web_id: str


class UserGet(UserPost):
    id: int


class SpamPost(Base):
    user_link: HttpUrl


class SpamGet(SpamPost):
    id: int


class VideoPost(Base):
    link: HttpUrl
    request: str | None
    direction_id: int
    request_type: RequestTypes


class VideoGet(VideoPost):
    id: int


class ResponsePost(Base):
    content: str | None
    video_id: int
    user_id: int


class ResponseGet(ResponsePost):
    id: int


class DirectionPost(Base):
    link: HttpUrl
    name: Directions


class DirectionGet(DirectionPost):
    id: int

