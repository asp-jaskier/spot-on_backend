from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Table, JSON, Enum, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base
from datetime import datetime, timedelta, date

perms = ['user', 'moderator', 'admin', 'owner']
gender = ["male", "female", "other"]


class User(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True, index=True)
    username=Column(String(50), unique=True, nullable=False)
    email=Column(String(100), unique=True, nullable=False)
    password=Column(String(200), nullable=False)
    # info
    name = Column(String(200), unique=False, nullable=False)
    gender = Column(Enum(*gender, name="gender_enum"))
    age = Column(Integer, unique=False, nullable=False)
    perm = Column(Enum(*perms, name="permission_enum"), default='user')
    country = Column(String(50), unique=False, nullable=False, default='Unknown')
    security_char = Column(String(24))

    #platform things
    account_level = Column(Integer, unique=False, nullable=False, default=1)
    xp_have = Column(Integer, unique=False, nullable=False, default=1)

class Email_verify_requests(Base):
    __tablename__ = 'verify_requests'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(250), nullable=False, unique=False)
    code = Column(String(20), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    expiry_at = Column(DateTime, default= datetime.utcnow() + timedelta(hours=24), nullable=False)

# else

