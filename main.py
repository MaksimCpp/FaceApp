# ---------------------------------
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Тут неструктурированная сборная солянка
# Весь структурированный код в каталоге src
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ---------------------------------


from typing import List, Optional
from dataclasses import dataclass
from loguru import logger

from insightface.app import FaceAnalysis
import numpy as np
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine
)
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from datetime import datetime

import argparse
import cv2
import asyncio

Base = declarative_base()

engine = create_async_engine("postgresql+asyncpg://user:password@host:port/name")
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)

face_app = FaceAnalysis(
    name='buffalo_l',
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'],
    allowed_modules=['detection', 'recognition']
)
face_app.prepare(ctx_id=0, det_size=(640, 640))


class FaceService:
    def __init__(self):
        self._face_app = FaceAnalysis(
            name='buffalo_l',
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider'],
            allowed_modules=['detection', 'recognition']
        )
        self._face_app.prepare(ctx_id=0, det_size=(640, 640))

    def get_faces(self, image):
        return self._face_app.get(image)


class Personal(Base):
    __tablename__ = "personal"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[List[float]] = mapped_column(Vector(512))


@dataclass
class PersonalDTO:
    id: int
    full_name: str
    embedding: Optional[List[float]] = None


async def find_match(embedding: List[float]):
    async with sessionmaker() as session:
        query = select(
            Personal
        ).where(
            (1 - Personal.embedding.cosine_distance(embedding)) > 0.5
        ).order_by(
            Personal.embedding.cosine_distance(embedding)
        ).limit(1)

        result = await session.execute(query)
        personal = result.scalar_one_or_none()

        if personal is not None:
            logger.debug("Похожий человек обнаружен")
            return PersonalDTO(
                id=personal.id,
                full_name=personal.full_name
            )
        
        logger.debug("Похожий человек не обнаружен")
        return None

async def recognize_face(location: str):
    face_service = FaceService()
    video = cv2.VideoCapture(0)
    while video.isOpened():
        ret, image = video.read()
        if not ret:
            logger.error("Error.")

        # image = cv2.imread('максон.jpg')
        faces = face_service.get_faces(image)
        if len(faces) == 0:
            logger.info('На видео нет лиц')
            continue

        # main_face = max(
        #     faces,
        #     key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
        # )
        for face in faces:
            embedding = face.embedding.astype(np.float32).tolist()
            personal = await find_match(embedding)
            if personal is None:
                continue

            print({
                'name': personal.full_name,
                'location': location,
                'datetime': str(datetime.now())
            })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Описание программы")
    parser.add_argument(
        '-l', '--location', 
        type=str, 
        help="Аудитория нахождения камеры", 
        default='1-218'
    )
    args = parser.parse_args()
    asyncio.run(recognize_face(args.location))
