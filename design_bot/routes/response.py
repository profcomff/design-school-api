import os.path
import random
import string
from http.client import HTTPException

import aiofiles
from fastapi import APIRouter, UploadFile, File
from fastapi_sqlalchemy import db
from pydantic import parse_obj_as
from starlette.responses import PlainTextResponse

from design_bot.exceptions import ObjectNotFound
from design_bot.models.db import User, Video, Direction, Response
from .models.models import VideoPost, VideoGet, ResponsePost, ResponseGet
from design_bot.settings import get_settings
from design_bot.methods.google_drive import upload_file_to_drive, upload_text_to_drive

settings = get_settings()

response = APIRouter(prefix="/response/{user_id}", tags=["Response"])


@response.post("/file", response_model=ResponseGet)
async def upload_file(user_id: int, response_inp: ResponsePost, file: UploadFile = File(...)) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != response_inp.video_id:
            raise HTTPException(403, "Forbidden")
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(12))
    ext = file.filename.split('.')[-1]
    path = os.path.join(settings.FILE_PATH,
                        f"{user.first_name}_{user.middle_name}_{user.last_name}_video_{next_video.id}_{random_string}.{ext}")
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    link = await upload_file_to_drive(user.folder_id, path)
    db.session.add(response := Response(**response_inp.dict(), content=link))
    db.session.flush()
    return ResponseGet.from_orm(response)


@response.post("/video", response_model=ResponseGet)
async def upload_link(user_id: int, response_inp: ResponsePost) -> ResponseGet:
    if "drive.google.com" not in response_inp.content:
        raise HTTPException(422, "Invalid content, only GDrive is correct")
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != response_inp.video_id:
            raise HTTPException(403, "Forbidden")
    link = await upload_text_to_drive(**response_inp.dict(), social_web_id=user.social_web_id,
                                      user_folder_id=user.folder_id,
                                      lesson_number=next_video.id)
    db.session.add(response := Response(user_id=user.id, video_id=response_inp.video_id, content=link))
    db.session.flush()
    return ResponseGet.from_orm(response)


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
    link = await upload_text_to_drive(**response_inp.dict(), social_web_id=user.social_web_id,
                                      user_folder_id=user.folder_id,
                                      lesson_number=next_video.id)
    db.session.add(response := Response(user_id=user.id, video_id=response_inp.video_id, content=link))
    db.session.flush()
    return ResponseGet.from_orm(response)
