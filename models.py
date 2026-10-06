from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Table, JSON, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field


from database import Base
from datetime import datetime, timedelta, date

perms = ['user', 'moderator', 'admin', 'owner']
gender = ["male", "female", "other"]
event_types = ["drift", "car_meet", "race"]
rarity_types = [
    "Common",
    "Sports Car",
    "Performance",
    "Supercar",
    "Exotic",
    "Hypercar",
    "One-of-One",
]

# car_tags = [
#     "JDM",
#     "Euro",
#     "American",
#     "Classic",
#     "Luxury",
#     "Electric",
#     "SUV",
#     "Wagon",
#     "Convertible",
# ]

##### TABELE POŚREDNIE ########

event_users = Table(
    "event_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
)

###############################

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

    #thigs
    xp_have = Column(Integer, unique=False, nullable=False, default=1)

    #powiezania
    events = relationship(
        "Event",
        secondary=event_users,
        back_populates="users"
    )
    spots = relationship("Spot", back_populates="user")

class Email_verify_requests(Base):
    __tablename__ = 'verify_requests'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(250), nullable=False, unique=False)
    code = Column(String(20), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    expiry_at = Column(DateTime, default= datetime.utcnow() + timedelta(hours=24), nullable=False)

# else
######################################

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)

    photo_path = Column(String(100), unique=True, nullable=False)
    brand = Column(String(70), unique=False, nullable=False)
    model = Column(String(100), unique=True, nullable=False)
    rarity = Column(Enum(*rarity_types, name="rarity_enum"), unique=False, nullable=False)
    tags = Column(JSON, unique=False, nullable=True)

    spots = relationship("Spot", back_populates="car")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(Enum(*event_types, name="event_type_enum"), unique=False, nullable=False)
    photo_url = Column(String(100), unique=False, nullable=True)
    name = Column(String(100), unique=False, nullable=False)
    date = Column(DateTime, nullable=False)
    localization = Column(JSON, unique=False, nullable=False)
    description = Column(String(2000), unique=False, nullable=True)
    users = relationship(
        "User",
        secondary=event_users,
        back_populates="events"
    )

class Spot(Base):
    __tablename__ = "spots"
    id = Column(Integer, primary_key=True, index=True)

    time = Column(DateTime, nullable=False)
    localization = Column(JSON, unique=False, nullable=False)

    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car = relationship("Car", back_populates="spots")
    user = relationship("User", back_populates="spots")

    # metadata
    photo_path = Column(String(100), unique=False, nullable=False)



