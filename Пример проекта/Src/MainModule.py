from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from models import Image
from schemas import ImageCreate, ImageResponse, ImageUpdateType, ImageUpdatePath
from database import get_db
from image_utils import convert_image, get_image_metadata

app = FastAPI(title="Image Processing API")

# Папка для хранения изображений
UPLOAD_DIR = "images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# POST: Добавление изображения
@app.post("/api/image/add", response_model=ImageResponse)
async def add_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_extension = file.filename.rsplit(".", 1)[-1].lower()
    if file_extension not in ["jpg", "png"]:
        raise HTTPException(status_code=400, detail="Только JPG и PNG файлы разрешены")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size, width, height = get_image_metadata(file_path)

    db_image = Image(
        name=file.filename,
        size=size,
        resolution_width=width,
        resolution_height=height,
        file_type=file_extension,
        file_path=file_path
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# PUT: Изменение расширения файла (PNG to JPG, JPG to PNG)
@app.put("/api/image/change/type/{image_id}", response_model=ImageResponse)
async def change_image_type(image_id: int, update: ImageUpdateType, db: Session = Depends(get_db)):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Изображение не найдено")

    if update.file_type.lower() not in ["jpg", "png"]:
        raise HTTPException(status_code=400, detail="Поддерживаются только форматы JPG и PNG")

    if db_image.file_type.lower() == update.file_type.lower():
        raise HTTPException(status_code=400, detail="Изображение уже в этом формате")

    new_file_path = convert_image(db_image.file_path, update.file_type)
    size, width, height = get_image_metadata(new_file_path)

    # Удаляем старый файл
    os.remove(db_image.file_path)

    # Обновляем данные в базе
    db_image.file_path = new_file_path
    db_image.file_type = update.file_type.lower()
    db_image.size = size
    db_image.resolution_width = width
    db_image.resolution_height = height

    db.commit()
    db.refresh(db_image)
    return db_image

# PUT: Перемещение изображения в другую папку
@app.put("/api/image/change/path/{image_id}", response_model=ImageResponse)
async def change_image_path(image_id: int, update: ImageUpdatePath, db: Session = Depends(get_db)):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Изображение не найдено")

    new_dir = update.new_path
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    new_file_path = os.path.join(new_dir, db_image.name)
    shutil.move(db_image.file_path, new_file_path)

    db_image.file_path = new_file_path
    db.commit()
    db.refresh(db_image)
    return db_image

# GET: Получить все изображения
@app.get("/api/image", response_model=List[ImageResponse])
async def get_all_images(db: Session = Depends(get_db)):
    images = db.query(Image).all()
    return images

