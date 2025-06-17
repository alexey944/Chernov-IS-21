from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Image(Base):
    tablename = "images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    size = Column(Integer)  # Размер в байтах
    resolution_width = Column(Integer)
    resolution_height = Column(Integer)
    file_type = Column(String)  # Тип файла (png, jpg, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String)  # Путь к файлу