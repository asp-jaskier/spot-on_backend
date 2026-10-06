from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class AddSpot(BaseModel):
    token: str
    time: datetime
    localization: tuple[float, float]
    car_id: int

class ViewSpot(BaseModel):
    token: str
    spot_id: int