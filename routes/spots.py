from datetime import timedelta, datetime, date
from typing import Annotated
from urllib import request
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from settings import static_vars

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
from schemas.spot import AddSpot, ViewSpot

router = InferringRouter(prefix="/spots-api", tags=["spots"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@cbv(router)
class spots_api:
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

    @router.post("/add_spot", status_code=status.HTTP_201_CREATED)
    async def add_spot(self, request: str = Form(...), photo: UploadFile = File(...)):
        try:
            request = AddSpot.model_validate_json(request)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())

        db = self.db_dependency

        user = await self.get_user(request.token)

        car = db.query(models.Car).filter(models.Car.id == request.car_id).first()
        if car is None:
            raise HTTPException(
                status_code=404, detail="Car with that car id not found"
            )

        extension = Path(photo.filename).suffix
        filename = f"{uuid4()}{extension}"

        # pełna ścieżka do zapisu
        photo_path = static_vars.spots_photos_path / filename

        with photo_path.open("wb") as buffer:
            buffer.write(await photo.read())

        new_spot = models.Spot(
            time=request.time,
            localization=request.localization,
            car=car,
            user=user,
            photo_path=str(filename),
        )

        db.add(new_spot)
        db.commit()
        db.refresh(new_spot)

        return {"msg": "success", "id": new_spot.id}

    @router.post("/view_spot", status_code=status.HTTP_200_OK)
    async def get_spot_info(self, request: ViewSpot):
        db = self.db_dependency

        user = await self.get_user(request.token)

        spot = db.query(models.Spot).filter(models.Spot.id == request.spot_id).first()
        if not spot:
            raise HTTPException(status_code=404, detail="Spot not found")

        times_spotted = (
            db.query(models.Spot)
            .join(models.Car)
            .filter(models.Car.model == spot.car.model)
            .count()
        )

        data = {
            "photo": spot.photo_path,
            "car_brand": spot.car.brand,
            "car_model": spot.car.model,
            "time": spot.time,
            "times_spotted": times_spotted,
        }

        return {"msg": "success", "data": data}
