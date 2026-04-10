import argparse
import asyncio
from datetime import datetime

import cv2
import numpy as np

from loguru import logger

from face.service import FaceService
from infrastructure.databases.postgresql.database import (
    create_tables, sessionmaker, engine
)
from infrastructure.repositories.postgresql.personal.implementation import PostgreSQLPersonalRepository


async def recognize_face(location: str):
    await create_tables(engine)
    async with sessionmaker() as session:
        repository = PostgreSQLPersonalRepository(session)
        face_service = FaceService()
        video = cv2.VideoCapture(0)
        while video.isOpened():
            ret, image = video.read()
            if not ret:
                logger.error("Error.")

            faces = face_service.get_faces(image)
            if len(faces) == 0:
                logger.info('На видео нет лиц')
                continue

            """
            Тут 2 варианта
            1 ищет среди всех лиц, которые сейчас видит камеры берет то,
            , что ближе к камере:
            main_face = max(
                faces,
                key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
            )
            embedding = main_face.embedding.astype(np.float32).tolist()
            personal = await repository.find_by_embedding(embedding)
            if personal is None:
                continue

            print({
                'name': personal.full_name,
                'location': location,
                'datetime': str(datetime.now())
            })

            2 берет все лица на камере и ищет их:
            for face in faces:
                embedding = face.embedding.astype(np.float32).tolist()
                personal = await repository.find_by_embedding(embedding)
                if personal is None:
                    continue
            """

            # Варианты вставлять в этот промежуток
            # ------------------------------------
            for face in faces:
                embedding = face.embedding.astype(np.float32).tolist()
                personal = await repository.find_by_embedding(embedding)
                if personal is None:
                    continue

                """
                На твой сервис по сути должны уходить такие данные:
                {
                    "embedding": list[float],   - вектор лица студента
                    "location": str,            - аудитория
                    "datetime": datetime        - дата и время распознавания
                }
                """

                # Здесь вместо вектора имя из моей тестовой базы
                print({
                    'name': personal.full_name,
                    'location': location,
                    'datetime': str(datetime.now())
                })
            # ------------------------------------

if __name__ == '__main__':
    # В параметрах вводим аудиторию, в которой находитя камера
    parser = argparse.ArgumentParser(description="Описание программы")
    parser.add_argument(
        '-l', '--location', 
        type=str, 
        help="Аудитория нахождения камеры", 
        default='1-218'
    )
    args = parser.parse_args()
    asyncio.run(recognize_face(args.location))
