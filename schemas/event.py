from datetime import datetime
from pydantic import BaseModel
from typing import List, Literal, Optional
from models import event_types


class AddEvent(BaseModel):
    token: str
    time: datetime
    localization: tuple[float, float]
    car_id: int
    name: str
    description: str
    event_type: Literal[*event_types]
