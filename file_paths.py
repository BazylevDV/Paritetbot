import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Определение корневой директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути к файлам
FILE_PATHS = {
    "catalog": os.path.join(BASE_DIR, "app", "files", "catalog", "Паритет_Диагностическое оборудование_2023 (2).pdf"),
    "warehouse": os.path.join(BASE_DIR, "app", "files", "stock", "Паритет _Спец и Склад _Q3-Q4.24.pdf"),
    "promo1": os.path.join(BASE_DIR, "app", "files", "promo", "Копия КП_Спец предложение__GE Versana Active_2024-09-30.xls"),
    "promo2": os.path.join(BASE_DIR, "app", "files", "promo", "Копия КП_СЦИ Millennium исп.1 на базе DX-M с АРМ_октябрь 2024.xls"),
}

# MIME-типы файлов
MIME_TYPES = {
    "catalog": 'application/pdf',
    "warehouse": 'application/pdf',
    "promo1": 'application/vnd.ms-excel',
    "promo2": 'application/vnd.ms-excel',
}

# Проверка существования файлов
for file_type, file_path in FILE_PATHS.items():
    logger.info(f"Проверка пути к файлу: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

def MIME_TYP():
    return None