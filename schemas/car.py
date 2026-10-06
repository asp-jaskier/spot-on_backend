from typing import List, Literal, Optional
from pydantic import BaseModel
from models import rarity_types


class CarCreate(BaseModel):
    photo_path: str
    brand: str
    model: str
    rarity: Literal[*rarity_types]
    tags: Optional[List[str]] = None
