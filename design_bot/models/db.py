from __future__ import annotations
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
    SIXTH = "2v"


class RequestType(str, Enum):
    PHOTO = "photo"
    CONTENT = "content"
    SOCIALWEBDESIGN = "socialwebdesign"
    IDENTICDESIGN = "identicdesign"


class SpamBeforeRegistration(Base):
    id = Column(Integer, primary_key=True)
    user_link = Column(String, nullable=False)


class Direction(Base):
    id = Column(Integer, primary_key=True)
    link = Column(String, nullable=False)
    name = Column(String, nullable=False)

    users: list[User] = relationship("User", foreign_keys="User.direction_id")
    videos: list[Video] = relationship("Video", foreign_keys="Video.direction_id")



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


class Video(Base):
    id = Column(Integer, primary_key=True)
    request = Column(Text, nullable=True)
    direction_id = Column(Integer, ForeignKey("direction.id"))
    request_type = Column(DbEnum(Year, native_enum=False), nullable=True)

    direction: Direction = relationship("Direction", foreign_keys=[direction_id], back_populates="videos")


class Response(Base):
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=True)
    video_id = Column(Integer, ForeignKey("video.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    video: Video = relationship("Video", foreign_keys=[video_id])
    user: User = relationship("User", foreign_keys=[user_id])
