from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from design_bot.models.db import Direction
from .models.models import DirectionPost, DirectionGet
from ..methods import auth

directions = APIRouter(prefix="/directions", tags=["Directions"])


@directions.post("/", response_model=DirectionPost)
async def create_direction(direction_inp: DirectionPost, _: auth.User = Depends(auth.get_current_user)) -> DirectionGet:
    db.session.add(direction := Direction(**direction_inp.dict()))
    db.session.flush()
    return DirectionGet.from_orm(direction)


