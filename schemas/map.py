from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class GetMarkers(BaseModel):
    token: str
    localization: tuple[float, float]
    radius_km: Optional[int] = None