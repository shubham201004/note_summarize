# schemas.py
from pydantic import BaseModel

class ItemResponse(BaseModel):
    title: str
    description: str

    class Config:
        from_attributes  = True
