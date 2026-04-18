import os
import requests
import time
import pandas as pd
from tqdm import tqdm
from pydub import AudioSegment
from io import BytesIO
import logging

#FFmpeg для конвертации в wav и изменения частоты
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

#конфигурация
API_KEY = "GHpvWvbBZxIWuKqNZrUXuam4dGrQcGHWoihXCl9y"
OUTPUT_DIR = "downloaded_birds"
CSV_PATH = "data/UrbanSound8k+birds/downloaded_birds/birds.csv"
TARGET_SR = 22050
MAX_DURATION = 4.0
PAGE_SIZE = 30  # Количество результатов на страницу

#создание папки
os.makedirs(OUTPUT_DIR, exist_ok=True)

#настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_audio_from_memory(sound_id):
    try:
        # 1.получаем метаданные
        info_url = f"https://freesound.org/apiv2/sounds/{sound_id}/"
        params = {"token": API_KEY, "fields": "id,previews,duration,tags,username"}
        response = requests.get(info_url, params=params)
        sound_info = response.json()

        #проверка длительности
        if sound_info["duration"] > MAX_DURATION:
            return None

        # 2.скачиваем аудио прямо в память
        download_url = sound_info["previews"]["preview-hq-mp3"]
        audio_response = requests.get(download_url)
        audio_response.raise_for_status()

        # 3.обрабатываем в памяти (без временных файлов)
        with BytesIO(audio_response.content) as audio_stream:
            audio = AudioSegment.from_file(audio_stream)
            audio = audio.set_frame_rate(TARGET_SR).set_channels(1)

            if len(audio) > MAX_DURATION * 1000:
                audio = audio[:int(MAX_DURATION * 1000)]

            # 4.сохраняем результат
            filename = f"{sound_info['username']}_{sound_id}.wav"
            output_path = os.path.join(OUTPUT_DIR, filename)
            audio.export(output_path, format="wav")

            return {
                "filename": filename,
                "duration": len(audio) / 1000,
                "tags": sound_info.get("tags", []),
                "id": sound_id
            }

    except Exception as e:
        logger.error(f"Ошибка обработки {sound_id}: {str(e)}")
        return None


def main():
    csv_data = {
        "slice_file_name": [],
        "fsID": [],
        "start": [],
        "end": [],
        "salience": [],
        "fold": [],
        "class": [],
        "species": []
    }

    downloaded = 0
    page = 1

    try:
        while downloaded < 800:
            #поиск на Freesound
            search_url = "https://freesound.org/apiv2/search/text/"
            params = {
                "query": "bird",
                "filter": f"duration:[0 TO {MAX_DURATION}]",
                "fields": "id",
                "page_size": PAGE_SIZE,
                "page": page,
                "token": API_KEY
            }

            response = requests.get(search_url, params=params)
            data = response.json()

            if not data.get("results"):
                logger.info("Больше результатов нет")
                break

            #обработка каждого результата
            for sound in tqdm(data["results"], desc=f"Страница {page}"):
                if downloaded >= 800:
                    break

                result = process_audio_from_memory(sound["id"])
                if result:
                    #заполняем CSV структуру
                    csv_data["slice_file_name"].append(result["filename"])
                    csv_data["fsID"].append(f"fs_{result['id']}")
                    csv_data["start"].append(0.0)
                    csv_data["end"].append(result["duration"])
                    csv_data["salience"].append(1)
                    csv_data["fold"].append((downloaded % 10) + 1)
                    csv_data["class"].append("bird")
                    csv_data["species"].append(result["tags"][0] if result["tags"] else "unknown")

                    downloaded += 1
                    logger.info(f"Успешно: {downloaded}/10")

                    #задержка для API
                    time.sleep(1)

            page += 1

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")

    #сохранение результатов
    if downloaded > 0:
        pd.DataFrame(csv_data).to_csv(CSV_PATH, index=False)
        logger.info(f"Готово! Скачано {downloaded} файлов.")
    else:
        logger.error("Не удалось скачать файлы")


if __name__ == "__main__":
    main()


