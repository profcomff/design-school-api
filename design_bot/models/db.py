from __future__ import annotations

from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy import Enum as DbEnum
from enum import Enum
from sqlalchemy.orm import relationship


class Year(str, Enum):
    FIRST = "1"
    SECOND = "2"
    THIRD = "3"
    FOURTH = "4"
    FIFTH = "1м"
    SIXTH = "2м"


class Directions(str, Enum):
    PHOTO = "PHOTO"
    CONTENT = "CONTENT"
    SOCIALWEBDESIGN = "SOCIALWEBDESIGN"
    IDENTICDESIGN = "IDENTICDESIGN"


class RequestTypes(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    FILE = "file"


class SpamBeforeRegistration(Base):
    id = Column(Integer, primary_key=True)
    user_link = Column(String, nullable=False)


class Direction(Base):
    id = Column(Integer, primary_key=True)
    link = Column(String, nullable=False)
    name = Column(String, nullable=False)

    users: list[User] = relationship("User", foreign_keys="User.direction_id")
    videos: list[Video] = relationship("Video", foreign_keys="Video.direction_id",  back_populates="direction", order_by=lambda: Video.id)

    @hybrid_property
    def last_video(self):
        return self.videos[-1] if len(self.videos) else None


class User(Base):
    id = Column(Integer, primary_key=True)
    union_id = Column(Integer, nullable=False)
    direction_id = Column(Integer, ForeignKey("direction.id"))
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    year = Column(DbEnum(Year, native_enum=False), nullable=False)
    readme = Column(Text, nullable=True)
    link = Column(String, nullable=False)

    direction: Direction = relationship("Direction", foreign_keys=[direction_id], back_populates="users")
    responses: list[Response] = relationship("Response", foreign_keys="Response.user_id", back_populates="user")

    @hybrid_property
    async def last_response(self) -> Response:
        return sorted(self.responses, key=lambda response: response.video_id)[-1]

    @hybrid_property
    async def next_user_video(self) -> Video:
        last_response = await self.last_response
        if last_response:
            return last_response.video.next_video
        return self.direction.videos[0]


class Video(Base):
    id = Column(Integer, primary_key=True)
    next_video_id = Column(Integer, ForeignKey("video.id"))
    link = Column(String, nullable=False)
    request = Column(Text, nullable=True)
    direction_id = Column(Integer, ForeignKey("direction.id"))
    request_type = Column(DbEnum(RequestTypes, native_enum=False), nullable=True)

    direction: Direction = relationship("Direction", foreign_keys=[direction_id], back_populates="videos")

    prev_video: Video
    next_video: Video = relationship("Video", foreign_keys=[next_video_id], backref="prev_video", remote_side=id)


class Response(Base):
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=True)
    video_id = Column(Integer, ForeignKey("video.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    video: Video = relationship("Video", foreign_keys=[video_id])
    user: User = relationship("User", foreign_keys=[user_id], back_populates="responses")
