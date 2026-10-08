from datetime import timedelta, datetime, date
from typing import Annotated
from urllib import request
from pathlib import Path
from uuid import uuid4
from settings import static_vars


from fastapi import WebSocket, APIRouter, Depends, HTTPException, Request, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
import models
from sqlalchemy import exc
from sqlalchemy.orm.attributes import flag_modified
from routes.auth import get_current_user
from schemas.user import GetInfo
from schemas.car import CarCreate

router = InferringRouter(prefix="/cars-api", tags=["cars"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@cbv(router)
class cars_api:
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

    @router.get("/get_brands", status_code=status.HTTP_200_OK)
    async def get_brands(self):
        db = self.db_dependency
        raw_brands = db.query(models.Car.brand).distinct().all()
        brands = [b[0] for b in raw_brands]
        return brands

    @router.get("/get_car", status_code=status.HTTP_200_OK)
    async def get_car(self, car_id: int):
        db = self.db_dependency
        data_row = db.query(models.Car).filter(models.Car.id == car_id).first()
        if not data_row:
            raise HTTPException(status_code=404, detail="User not found")

        data = []
        data.append(
            {
                "id": data_row.id,
                "brand": data_row.brand,
                "model": data_row.model,
                "rarity": data_row.rarity,
                "tags": data_row.tags,
            }
        )

        return data

    @router.get("/get_models/{brand}", status_code=status.HTTP_200_OK)
    async def get_models(self, brand: str):
        db = self.db_dependency
        raw_models = db.query(models.Car.model).filter(models.Car.brand == brand).all()
        models_d = [b[0] for b in raw_models]
        return models_d

    @router.post("/add_car", status_code=status.HTTP_201_CREATED, response_model=None)
    async def add_car(self, request: CarCreate):
        db = self.db_dependency

        user = await self.get_user(request.token)

        extension = Path(request.model).suffix
        filename = f"{uuid4()}{extension}"

        photo_path = str(static_vars.cars_photos_path / filename)
        new_car = models.Car(
            photo_path=photo_path,
            brand=request.brand,
            model=request.model,
            rarity=request.rarity,
            tags=request.tags,
        )
        try:
            db.add(new_car)
            db.commit()
            db.refresh(new_car)
        except exc.IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Taki model juz istanieje",
            )
        return {"msg": "Pomyślnie dodano do bazy danych", "id": new_car.id}
