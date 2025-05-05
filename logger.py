import logging
import sys

# Создаём логгер
logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

# 🔸 Формат логов
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 🔹 Файл логов
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# 🔹 Вывод в терминал
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Добавляем обработчики
logger.addHandler(file_handler)
logger.addHandler(console_handler)
