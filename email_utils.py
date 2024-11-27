import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from email.header import Header
import aiosmtplib

# Импортируем пути к файлам и MIME-типы
from app.file_paths import FILE_PATHS, MIME_TYPES
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email.utils import formataddr
from email.header import Header
import aiosmtplib
import os
from app.file_paths import FILE_PATHS, MIME_TYPES  # Импортируем переменные

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Функция для отправки письма
async def send_email(recipient, subject, body, file_type):
    # Настройки SMTP сервера
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "dmbazylev@gmail.com"
    smtp_password = "vixy voez jfih mixv"  # Замените на сгенерированный пароль приложения

    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = formataddr(('Паритет', smtp_username))
    msg['To'] = formataddr(('Получатель', recipient))
    msg['Subject'] = Header(subject, 'utf-8').encode()
    msg.set_charset('utf-8')  # Установка кодировки UTF-8

    msg.attach(MIMEText(body, 'plain', 'utf-8'))  # Установка кодировки UTF-8 для тела письма

    # Прикрепление файла, если указан тип файла
    if file_type and file_type in FILE_PATHS:
        file_path = FILE_PATHS[file_type]
        mime_type = MIME_TYPES[file_type]
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                part.add_header('Content-Type', mime_type)  # Установка MIME-типа
                msg.attach(part)
        else:
            logger.error(f"File not found: {file_path}")

    # Отправка письма
    try:
        logger.info(f"Sending email to {recipient} with subject: {subject}")
        await aiosmtplib.send(msg, hostname=smtp_server, port=smtp_port, username=smtp_username, password=smtp_password,
                              start_tls=True)
        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")