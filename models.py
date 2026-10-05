from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Table, JSON, Enum, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base
from datetime import datetime, timedelta, date

perms = ['user', 'moderator', 'admin', 'owner']
gender = ["male", "female", "other"]

exercise_types = ["demo", "exercise", "test", "challenge", "practice"]

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

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), unique=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)
    difficulty = Column(Integer, unique=False, nullable=False, default=1)
    subcategories = relationship(
        "SubCategory",
        back_populates="category"
    )

class SubCategory(Base):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), unique=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)
    difficulty = Column(Integer, unique=False, nullable=False, default=1)

    category = relationship(
        "Category",
        back_populates="subcategories"
    )

    exercises = relationship(
        "Exercise",
        back_populates="subcategory"
    )

class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True, index=True)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(Enum(*exercise_types, name="exercise_type_enum"), default="exercise", nullable=False)
    description = Column(String(500), unique=False, nullable=True)
    examples = Column(JSON, unique=False, nullable=True)
    correct_regex = Column(String(200), unique=False, nullable=True)
    preview_examples = Column(JSON, unique=False, nullable=True)

    subcategory = relationship(
        "SubCategory",
        back_populates="exercises")