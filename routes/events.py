from datetime import timedelta, datetime, date
from typing import Annotated
from urllib import request

from fastapi import (
    WebSocket,
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File,
    Form,
)
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import models
from sqlalchemy.orm.attributes import flag_modified
from routes.auth import get_current_user
from schemas.user import GetInfo
from schemas.event import AddEvent
from settings import static_vars
from pathlib import Path
from uuid import uuid4
from sqlalchemy import exc
from pydantic import ValidationError

router = InferringRouter(prefix="/user-api", tags=["user"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@cbv(router)
class events_api:
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

    @router.post("/add_event", status_code=status.HTTP_201_CREATED)
    async def add_event(self, request: str = Form(...), photo: UploadFile = File(...)):
        try:
            request = AddEvent.model_validate_json(request)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())

        db = self.db_dependency

        user = await self.get_user(request.token)

        extension = Path(photo.filename).suffix
        filename = f"{uuid4()}{extension}"

        photo_path = static_vars.events_photos_path / filename

        with photo_path.open("wb") as buffer:
            buffer.write(await photo.read())

        new_event = models.Event(
            photo_url=str(filename),
            name=request.name,
            date=request.time,
            localization=request.localization,
            description=request.description,
            event_type=request.event_type,
        )

        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        return {"msg": "success", "id": new_event.id}
