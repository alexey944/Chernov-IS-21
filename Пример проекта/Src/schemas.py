from pydantic import BaseModel
from datetime import datetime

class ImageBase(BaseModel):
    name: str
    file_type: str
    file_path: str

class ImageCreate(ImageBase):
    pass

class ImageUpdateType(BaseModel):
    file_type: str  # Новый тип файла (jpg или png)

class ImageUpdatePath(BaseModel):
    new_path: str  # Новый путь к файлу

class ImageResponse(ImageBase):
    id: int
    size: int
    resolution_width: int
    resolution_height: int
    created_at: datetime

    class Config:
        orm_mode = True