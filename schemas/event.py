from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from models import event_types


class AddEvent(BaseModel):
    token: str
    time: datetime
    localization: tuple[float, float]
    name: str
    description: str
    event_type: Literal[*event_types]
    event_end_at: datetime


class AddUserToEvent(BaseModel):
    token: str
    event_id: int