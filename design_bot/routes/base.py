from fastapi import FastAPI

from ..settings import Settings
from fastapi_sqlalchemy import DBSessionMiddleware

from .videos import videos
from .registration import registration
from .directions import directions
from .vk import bot_router

settings = Settings()
app = FastAPI()

app.add_middleware(
    DBSessionMiddleware,
    db_url=settings.DB_DSN,
    session_args={"autocommit": True},
)


app.include_router(directions)
app.include_router(videos)
app.include_router(registration)
app.include_router(bot_router)
