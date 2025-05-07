import logging
import os
from logging.handlers import RotatingFileHandler


logging.getLogger("aiogram.event").setLevel(logging.WARNING)
# Настройки логирования берутся из переменных окружения
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_DIR = os.getenv('LOG_DIR', 'logs')

# Создаем директорию для логов, если она не существует
os.makedirs(LOG_DIR, exist_ok=True)

# Формат вывода логов
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Ротация общего лога (INFO и выше)
info_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, 'bot.log'),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)
info_handler.setLevel(LOG_LEVEL)
info_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Ротация файла с ошибками (ERROR и выше)
error_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, 'bot_errors.log'),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Консольный вывод для отладки
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Конфигурация root-логгера
logging.basicConfig(level=LOG_LEVEL, handlers=[info_handler, error_handler, console_handler])

# Удобная функция для получения логгера модуля

def get_logger(name: str) -> logging.Logger:
    """Возвращает настроенный логгер для указанного имени"""
    return logging.getLogger(name)