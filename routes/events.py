from datetime import timedelta, datetime, date, timezone
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
from schemas.event import AddEvent, AddUserToEvent
from settings import static_vars
from pathlib import Path
from uuid import uuid4
from sqlalchemy import exc, func
from pydantic import ValidationError

router = InferringRouter(prefix="/events-api", tags=["events"])

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/Warsaw")


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(timezone.utc)

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

        start = to_utc(request.time)
        end = to_utc(request.event_end_at)

        if start < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Czas wydarzenia nie może być w przeszłości",
            )
        if end <= start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Koniec wydarzenia musi być po jego początku",
            )

        extension = Path(photo.filename).suffix
        filename = f"{uuid4()}{extension}"
        photo_path = static_vars.events_photos_path / filename
        with photo_path.open("wb") as buffer:
            buffer.write(await photo.read())

        new_event = models.Event(
            photo_url=str(filename),
            name=request.name,
            date=start,
            event_end_at=end,
            localization=request.localization,
            description=request.description,
            event_type=request.event_type,
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        return {"msg": "success", "id": new_event.id}

    @router.post("/add_user_to_event", status_code=status.HTTP_201_CREATED)
    async def add_user_to_event(self, request: AddUserToEvent):
        db = self.db_dependency
        user = await self.get_user(request.token)
        event = (
            db.query(models.Event).filter(models.Event.id == request.event_id).first()
        )
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        stmt = models.event_users.insert().values(
            user_id=user.id, event_id=request.event_id
        )

        try:
            db.execute(stmt)
            db.commit()
        except exc.IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="Użytkownik już dołączył do tego wydarzenia"
            )

        return {"msg": "User added to event successfully"}

    @router.get("/get_event/{event_id}", status_code=status.HTTP_200_OK)
    async def get_event(self, event_id: int):
        db = self.db_dependency
        result = (
            db.query(
                models.Event,
                func.count(models.event_users.c.user_id).label("participants_count"),
            )
            .outerjoin(
                models.event_users, models.Event.id == models.event_users.c.event_id
            )
            .filter(models.Event.id == event_id)
            .group_by(models.Event.id)
            .all()
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        events_list = []
        for event, count in result:
            events_list.append(
                {
                    "name": event.name,
                    "date": event.date,
                    "localization": event.localization,
                    "description": event.description,
                    "event_type": event.event_type,
                    "event_end_at": event.event_end_at,
                    "photo_url": event.photo_url,
                    "participants_count": count,
                }
            )

        return events_list