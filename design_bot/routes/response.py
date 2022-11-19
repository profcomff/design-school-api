import os.path
import random
import string

import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi import HTTPException
from fastapi_sqlalchemy import db

from design_bot.exceptions import ObjectNotFound
from design_bot.methods.google_drive import upload_file_to_drive, upload_text_to_drive
from design_bot.models.db import User, Response, RequestTypes
from design_bot.settings import get_settings
from .models.models import ResponsePost, ResponseGet
from ..methods import auth

settings = get_settings()

response = APIRouter(prefix="/video/{video_id}/response/{user_id}", tags=["Response"])


@response.post("/file", response_model=ResponseGet)
async def upload_file(
    user_id: int, video_id: int, file: UploadFile = File(...), _: auth.User = Depends(auth.get_current_user)
) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != video_id:
            raise HTTPException(403, "Forbidden, this video completed/not allowed")
        if next_video.request_type != RequestTypes.FILE:
            raise HTTPException(403, f"Forbidden, invalid video request type use {next_video.request_type} handler")
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(12))
    ext = file.filename.split('.')[-1]
    path = os.path.join(
        settings.FILE_PATH,
        f"{user.first_name}_{user.middle_name}_{user.last_name}_video_{next_video.id}_{random_string}.{ext}",
    )
    async with aiofiles.open(path, 'wb') as out_file:
        await out_file.write(await file.read())
        link = await upload_file_to_drive(
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            file_path=path,
            lesson_number=next_video.id,
            user_folder_id=user.folder_id,
            social_web_id=user.social_web_id,
        )
        db.session.add(response := Response(content=link, video_id=video_id, user_id=user.id))
        db.session.flush()
        os.remove(path)
    return ResponseGet.from_orm(response)


@response.post("/video", response_model=ResponseGet)
async def upload_link(
    user_id: int, video_id: int, response_inp: ResponsePost, _: auth.User = Depends(auth.get_current_user)
) -> ResponseGet:
    if "drive.google.com" not in response_inp.content:
        raise HTTPException(422, "Invalid content, only GDrive is correct")
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != video_id:
            raise HTTPException(403, "Forbidden, this video completed/not allowed")
        if next_video.request_type != RequestTypes.VIDEO:
            raise HTTPException(403, f"Forbidden, invalid video request type use {next_video.request_type} handler")
    link = await upload_text_to_drive(
        social_web_id=user.social_web_id,
        user_folder_id=user.folder_id,
        lesson_number=next_video.id,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        content=response_inp.content,
    )
    db.session.add(response := Response(user_id=user.id, video_id=video_id, content=link))
    db.session.flush()
    return ResponseGet.from_orm(response)


@response.post("/text", response_model=ResponseGet)
async def upload_text(
    user_id: int, video_id: int, response_inp: ResponsePost, _: auth.User = Depends(auth.get_current_user)
) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != video_id:
            raise HTTPException(403, "Forbidden, this video completed/not allowed")
        if next_video.request_type != RequestTypes.TEXT:
            raise HTTPException(403, f"Forbidden, invalid video request type use {next_video.request_type} handler")
    link = await upload_text_to_drive(
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        social_web_id=user.social_web_id,
        user_folder_id=user.folder_id,
        lesson_number=next_video.id,
        content=response_inp.content,
    )
    db.session.add(response := Response(user_id=user.id, video_id=video_id, content=link))
    db.session.flush()
    return ResponseGet.from_orm(response)


@response.post("/none", response_model=ResponseGet)
async def upload_none(user_id: int, video_id: int, _: auth.User = Depends(auth.get_current_user)) -> ResponseGet:
    user: User = db.session.query(User).get(user_id)
    if not user:
        raise ObjectNotFound(User, user_id)
    next_video = await user.next_user_video
    if not next_video:
        raise HTTPException(403, "Forbidden, Course ended")
    if next_video:
        if next_video.id != video_id:
            raise HTTPException(403, "Forbidden, this video completed/not allowed")
        if next_video.request_type:
            raise HTTPException(403, f"Forbidden, invalid video request type use {next_video.request_type} handler")
    db.session.add(response := Response(user_id=user.id, video_id=video_id, content=None))
    db.session.flush()
    return ResponseGet.from_orm(response)


@response.delete("/{id}", response_model=None)
async def delete_response(id: int, _: auth.User = Depends(auth.get_current_user)):
    res := Response = db.session.query(Response).get(id)
    if not res:
        raise ObjectNotFound(Response, id)
    db.session.delete(res)
    db.session.flush()
    return None
