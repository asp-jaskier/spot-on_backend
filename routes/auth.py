from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from models import User, Email_verify_requests

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

import random, string
import sqlalchemy
from settings import secret_key_token, algorithm
from utils.email_util import email_utils

email_utils_instance = email_utils()

from datetime import datetime, timedelta
from redis import Redis
from schemas.user import Token, UserBase, ChangePassword, verification_request, ResetPassBase

redis_conn = Redis(host='localhost', port=6379)

router = InferringRouter(
    prefix='/auth-api',
    tags=['auth']
)

SECRET_KEY = secret_key_token
ALGORITM = algorithm

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@cbv(router)
class auth_api():
    def __init__(self, db_dependency: db_dependency):
        self.db_dependency = db_dependency

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_User(user_request: UserBase, db: db_dependency):
    active_codes = db.query(Email_verify_requests).filter(models.Email_verify_requests.email == user_request.email).all()
    match_codes = 0
    for code in active_codes:
        if code.code == user_request.veryfication_code:
            match_codes = match_codes + 1
            active_code = code
    if match_codes == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Verification code is incorrect')
    if code.expiry_at <= datetime.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Code expired')
    old_user = db.query(User).filter(models.User.email == user_request.email).first()
    if old_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'User with that email already exist')
    old_user = db.query(User).filter(models.User.username == user_request.username.lower()).first()
    if old_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'User with that username already exist')
    if user_request.gender not in ['male', 'female']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Invalid gender entered')

    exclude = ["password", "veryfication_code", "username"]
    create_user_model = User(
        **user_request.dict(exclude=exclude),
        username=user_request.username.lower(),
        password=bcrypt_context.hash(user_request.password),
        perm='user',
        security_char=None,
    )
    try:
        db.add(create_user_model)
        db.commit()
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Invalid data')
    return {'msg': "success"}


async def scheuld_delete(id: int, time: int):
    import asyncio
    await asyncio.sleep(time)
    with Session(bind=engine) as session:
        email_requests = session.query(models.Email_verify_requests).filter(
            models.Email_verify_requests.id == id).first()
        if session:
            session.delete(email_requests)
            session.commit()
    print("Data processed:")


@router.post("/create_verification_request", status_code=status.HTTP_200_OK)
async def create_verification_request(request: verification_request, db: db_dependency, background_tasks: BackgroundTasks):
    pending_requests = db.query(Email_verify_requests).filter(models.Email_verify_requests.email == request.email).all()
    if len(pending_requests) > 2:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f'You have to many verification request to this email.')
    if not "@" and ".com" in request.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'That is not valid email, please enter correct email')
    probaly_request = True
    code = ""
    while probaly_request != None:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        probaly_request = db.query(models.Email_verify_requests).filter(
            models.Email_verify_requests.code == code).first()
    db_verify_request = Email_verify_requests(email=request.email, code=code)
    db.add(db_verify_request)
    db.commit()
    db.refresh(db_verify_request)
    # wysyłanie w tło usunięcie po 24h
    id = db_verify_request.id
    time_to_del = timedelta(hours=db_verify_request.expiry_at.hour).total_seconds()
    background_tasks.add_task(scheuld_delete, id, time_to_del)
    # wysyłanie maila
    massege = email_utils_instance.email_sent(email=request.email,
                                              topic="Verificaton code to CalIQ",
                                              data=f'''Your verification code is {code}\n
    Jeśli kod nie działa, poproś o nowy i wypróbuj te rozwiązania:
    Skorzystaj z przeglądarki w trybie incognito lub innej przeglądarki.
    Wyczyść pamięć podręczną przeglądarki i pliki cookie, a także wyłącz jej wszelkie dodatki i rozszerzenia.''')

    if massege == 'success':
        return {'msg': "success"}


@router.post("/login", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: db_dependency):
    user = auth_user(form_data.username.lower(), form_data.password, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    token = create_acces_token(user.username, user.id, timedelta(minutes=15), db=db)
    refresh_token = create_refresh_token(user.username, user.id, timedelta(hours=3), db=db)
    return {'access_token': token, 'token_type': 'bearer', 'refresh_token': refresh_token}

def auth_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_acces_token(username: str, user_id: int, expires_date: timedelta, db):
    encode = {'sub': username, 'id': user_id}
    user = db.query(User).filter(User.username == username).first()
    if expires_date != None:
        expires = datetime.utcnow() + expires_date
        encode.update({'exp': expires})
    if user.security_char == None:
        secure_code = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        updated_fields = {}
        updated_fields['security_char'] = secure_code
        db.query(User).filter(User.id == user_id).update(updated_fields)
        db.commit()
    else:
        secure_code = user.security_char
    encode.update({'security_char': secure_code})
    encode.update({'type': "access"})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)

def create_refresh_token(username: str, user_id: int, expires_date: timedelta, db):
    encode = {'sub': username, 'id': user_id}
    user = db.query(User).filter(User.username == username).first()
    if expires_date != None:
        expires = datetime.utcnow() + expires_date
        encode.update({'exp': expires})
    if user.security_char == None:
        secure_code = ''.join(random.choices(string.ascii_letters + string.digits, k=24))
        updated_fields = {}
        updated_fields['security_char'] = secure_code
        db.query(User).filter(User.id == user_id).update(updated_fields)
        db.commit()
    else:
        secure_code = user.security_char
    encode.update({'security_char': secure_code})
    encode.update({'type': "refresh"})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITM], options={"verify_exp": False})
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        sec_char: int = payload.get('security_char')
        expires: int = payload.get('exp')
        token_type: str = payload.get('type')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate user.')
            return False
        elif token_type != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Bad token type')
            return False
        elif not db.query(User).filter(User.id == user_id).first():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'User do not exist.')
            return False
        elif datetime.fromtimestamp(expires) < datetime.now():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Token expired') # do not change detail
            return False
        else:
            user = db.query(User).filter(User.id == user_id).first()
            if user.security_char != sec_char:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Token expired.')
        return {'username': username, 'id': user_id}
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate user.' + str(error))


@router.post("/delete_token/{token}", response_model=bool)
async def del_token(token: str, db: db_dependency):
    data = await get_current_user(token, db)
    if 'username' in data:
        id = data['id']
        user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        db.query(User).filter(User.id == id).update({'security_char': None})
        db.commit()
        return True
    else:
        False

@router.post("/refresh_token/", status_code=status.HTTP_200_OK)
async def refresh_token(token: str, db:db_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        sec_char: int = payload.get('security_char')
        expires: int = payload.get('exp')
        token_type: str = payload.get('type')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate user.')
            return False
        elif token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Bad token type')
            return False
        elif not db.query(User).filter(User.id == user_id).first():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'User do not exist.')
            return False
        elif expires is not None and datetime.utcfromtimestamp(expires) < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Token expired') # do not change detail
            return False
        else:
            user = db.query(User).filter(User.id == user_id).first()
            if user.security_char != sec_char:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Token expired.')
        access_token = create_acces_token(user.username, user.id, timedelta(minutes=15), db=db)
        return {"msg":"success", "access_token": access_token}
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate user.')


@router.post('/change_password', status_code=status.HTTP_200_OK)
async def change_password(db: db_dependency, request: ChangePassword):
    data = await get_current_user(request.token, db)
    if 'username' in data:
        id = data['id']
        user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    auth = auth_user(username=user.username, password=request.old_password, db=db)
    if auth == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    user.password = bcrypt_context.hash(request.new_password)
    try:
        db.commit()
        ignore = await del_token(token=request.token, db=db)
        return {'msg': "succes"}
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Invalid data')


@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def create_User(user_request: ResetPassBase, db: db_dependency):
    active_codes = db.query(Email_verify_requests).filter(
        models.Email_verify_requests.email == user_request.email).all()
    match_codes = 0
    for code in active_codes:
        if code.code == user_request.veryfication_code:
            match_codes = match_codes + 1
            active_code = code
    if match_codes == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Verification code is incorrect')
    if code.expiry_at <= datetime.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Code expired')
    # db_user = models.User(**user.dict(exclude='password'))
    user = db.query(models.User).filter(models.User.email == user_request.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    user.password = bcrypt_context.hash(user_request.new_password)
    try:
        db.commit()
        return {'msg': "succes"}
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Invalid data')