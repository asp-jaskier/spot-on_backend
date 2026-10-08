from datetime import timedelta, datetime, date
from typing import Annotated
from urllib import request
from fastapi.responses import StreamingResponse

from fastapi import WebSocket, APIRouter, Depends, HTTPException, Request, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import models
from sqlalchemy.orm.attributes import flag_modified
from routes.auth import get_current_user
from schemas.user import GetInfo
from pathlib import Path
from settings import static_vars

router = InferringRouter(prefix="/photos-api", tags=["photos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@cbv(router)
class photos_api:
    def __init__(self, db_dependency: db_dependency):
        self.db_dependency = db_dependency

    async def get_user(self, token):
        db = self.db_dependency
        data = await get_current_user(token=token, db=db)
        if "username" in data:
            username = data["username"]
            id = data["id"]
            user = db.query(models.User).filter(models.User.id == id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @router.get("/get_spots/{filename}")
    def get_spots(self, filename: str):
        file_path = Path(static_vars.spots_photos_path) / filename
        # return FileResponse(path=file_path, filename=filename, media_type='image/png')
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Spot image not found")
        file_stream = open(file_path, mode="rb")

        # Zwróć odpowiedź strumieniową
        return StreamingResponse(file_stream, media_type="image/png")

    @router.get("/get_events/{filename}")
    def get_events(self, filename: str):
        file_path = Path(static_vars.events_photos_path) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Event image not found")
        # return FileResponse(path=file_path, filename=filename, media_type='image/png')
        file_stream = open(file_path, mode="rb")

        # Zwróć odpowiedź strumieniową
        return StreamingResponse(file_stream, media_type="image/png")
