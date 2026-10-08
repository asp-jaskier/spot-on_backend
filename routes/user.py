from datetime import timedelta, datetime, date
from typing import Annotated
from urllib import request

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

router = InferringRouter(prefix="/user-api", tags=["user"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@cbv(router)
class users_api:
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

    @router.get("/get_user_data", status_code=status.HTTP_200_OK)
    async def get_user(self, token):
        db = self.db_dependency
        user_data = await get_current_user(token=token, db=db)
        user_id = (
            user_data["id"]
            if isinstance(user_data, dict)
            else getattr(user_data, "id", None)
        )

        data_row = db.query(models.User).filter(models.User.id == user_id).first()
        if not data_row:
            raise HTTPException(status_code=404, detail="User not found")

        data = []
        data.append(
            {
                "id": data_row.id,
                "username": data_row.username,
                "email": data_row.email,
                "name": data_row.name,
                "gender": data_row.gender,
                "age": data_row.age,
                "country": data_row.country,
            }
        )

        return data
