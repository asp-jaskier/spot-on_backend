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
from utils.level_utils import level_utils

router = InferringRouter(
    prefix='/user-api',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

lvl_utils_instance = level_utils()

@cbv(router)
class message_api():
    def __init__(self, db_dependency: db_dependency):
        self.db_dependency = db_dependency

    async def get_user(self, token):
        db = self.db_dependency
        data = await get_current_user(token=token, db=db)
        if 'username' in data:
            username = data['username']
            id = data['id']
            user = db.query(models.User).filter(models.User.id == id).first()
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        return user

    @router.post("/get_info", status_code=status.HTTP_200_OK)
    async def get_info(self, request: GetInfo):
        user = await self.get_user(token=request.token)
        xp_for_lvl = lvl_utils_instance.get_level_xp(int(user.account_level))
        data = {
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "age": user.age,
            "xp": user.xp_have,
            "lvl": user.account_level,
            "xp_for_lvl": xp_for_lvl,
            "country": user.country
        }
        return {"msg": "success", "data": data}

    @router.get("/get_user_profile", status_code=status.HTTP_200_OK)
    async def get_user_profile(self, username: str):
        db = self.db_dependency
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        xp_for_lvl = lvl_utils_instance.get_level_xp(int(user.account_level))
        data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "level": user.account_level,
            "xp": user.xp_have,
            "xp_for_lvl": xp_for_lvl,
            "country": user.country
        }
        return {"msg": "success", "data": data}