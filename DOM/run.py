"""

Подготовка виртуального окружения.
Запуск клиента.

"""

import os

import pygame

# CONFIG SETUP
# Путь к директории приложения
os.environ["APP_DIR"] = os.path.join(os.environ["LOCALAPPDATA"], "DOM")
if not os.path.exists(os.environ["APP_DIR"]):
    os.mkdir(os.environ["APP_DIR"])
# Путь к базе данных
os.environ["DB_PATH"] = os.path.join(os.environ["APP_DIR"], "database.sqlite")
# Путь к файлу отладки
os.environ["DEBUG_PATH"] = os.path.join(os.environ["APP_DIR"], "debug.log")
# Путь к файлу с данными аккаунта
os.environ["AUTH_PATH"] = os.path.join(os.environ["APP_DIR"], ".auth")
# Версия приложения
os.environ["VERSION"] = "0.0.0"
# Сервер
# os.environ["HOST"] = "http://127.0.0.1:5000"
os.environ["HOST"] = "https://dungeon-of-masters.herokuapp.com"

pygame.init()

info = pygame.display.Info()
# Разрешение монитора
os.environ["MAX_RESOLUTION"] = f"{info.current_w};{info.current_h}"

logger = __import__("logger").logger
__import__("database").Config.init()
__import__("main").main()

pygame.quit()

logger.info("Клиент закрыт")
