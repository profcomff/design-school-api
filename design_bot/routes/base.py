from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from ..settings import Settings
from fastapi_sqlalchemy import DBSessionMiddleware

from .videos import videos
from .registration import registration
from .directions import directions
from .auth import auth_router
from .uservideo import user_video
from .response import response

settings = Settings()
app = FastAPI()


class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_size: int) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == 'POST':
            if 'content-length' not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers['content-length'])
            if content_length > self.max_upload_size:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        return await call_next(request)


app.add_middleware(
    DBSessionMiddleware,
    db_url=settings.DB_DSN,
    session_args={"autocommit": True},
)

app.add_middleware(LimitUploadSize, max_upload_size=3145728)


app.include_router(directions)
app.include_router(auth_router)
app.include_router(videos)
app.include_router(registration)
app.include_router(user_video)
app.include_router(response)
