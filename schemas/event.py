from datetime import datetime
from pydantic import BaseModel
from typing import List, Literal, Optional
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
