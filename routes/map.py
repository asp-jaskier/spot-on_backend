from datetime import timedelta, datetime, date
from typing import Annotated
from urllib import request
import math
from sqlalchemy import cast, Float, func

from fastapi import WebSocket, APIRouter, Depends, HTTPException, Request, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import models
from schemas import event
from settings import static_vars
from sqlalchemy.orm.attributes import flag_modified
from routes.auth import get_current_user
from schemas.map import GetMarkers

router = InferringRouter(prefix="/map-api", tags=["map"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@cbv(router)
class map_api:
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

    @router.post("/get_markers", status_code=status.HTTP_200_OK)
    async def get_markers(self, request: GetMarkers):
        db = self.db_dependency
        user = await self.get_user(token=request.token)

        radius = request.radius_km or static_vars.radius_km_loading
        user_lat, user_lon = request.localization

        # Przelicznik kilometrów na stopnie GPS
        lat_delta = radius / 111.0
        lon_delta = radius / (111.0 * math.cos(math.radians(user_lat)))

        # .as_string() wymusza operator '->>' zamiast '->', zwracając tekst możliwy do rzutowania na Float
        spot_lat = models.Spot.localization[0].as_string().cast(Float)
        spot_lon = models.Spot.localization[1].as_string().cast(Float)

        now = datetime.now()

        data = []

        spots = (
            db.query(models.Spot)
            .filter(
                spot_lat >= user_lat - lat_delta,
                spot_lat <= user_lat + lat_delta,
                spot_lon >= user_lon - lon_delta,
                spot_lon <= user_lon + lon_delta,
                models.Spot.time >= now - timedelta(hours=1),
            )
            .all()
        )

        for spot in spots:
            data.append(
                {
                    "type": "spot",
                    "time": spot.time,
                    "localization": spot.localization,
                    "spot_id": spot.id,
                    "photo": spot.photo_path,
                }
            )
        event_lat = models.Event.localization[0].as_string().cast(Float)
        event_lon = models.Event.localization[1].as_string().cast(Float)

        events = (
            db.query(
                models.Event,
                func.count(models.event_users.c.user_id).label("participants_count"),
            )
            .outerjoin(
                models.event_users, models.Event.id == models.event_users.c.event_id
            )
            .filter(
                event_lat >= user_lat - lat_delta,
                event_lat <= user_lat + lat_delta,
                event_lon >= user_lon - lon_delta,
                event_lon <= user_lon + lon_delta,
                models.Event.event_end_at >= now,
            )
            .group_by(models.Event.id)
            .all()
        )

        for event, count in events:
            data.append(
                {
                    "type": "event",
                    "event_id": event.id,
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
        return {"msg": "success", "data": data}

