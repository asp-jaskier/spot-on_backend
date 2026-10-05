from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    name: str
    password: str
    veryfication_code: str
    gender: str
    age: int

class ResetPassBase(BaseModel):
    email: str
    new_password: str
    veryfication_code: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class verification_request(BaseModel):
    email: str

class ChangePassword(BaseModel):
    token: str
    old_password: str
    new_password: str

class updateUser(BaseModel):
    token: str
    request_code: str = None
    name: str = None
    username: str = None
    email: str = None

# user route

class GetInfo(BaseModel):
    token: str