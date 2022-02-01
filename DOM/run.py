"""

Подготовка виртуального окружения.
Запуск клиента.

"""

import argparse
import os

import pygame

parser = argparse.ArgumentParser()
parser.add_argument(
    "--env",
    default=r"{LOCALAPPDATA}\DOM",
    type=str,
    help="Путь к директории с файлами игры",
)
args = parser.parse_args()

# CONFIG SETUP
# Путь к директории приложения
os.environ["APP_DIR"] = args.env.format(**{k: v for k, v in os.environ.items()})
if not os.path.exists(os.environ["APP_DIR"]):
    os.mkdir(os.environ["APP_DIR"])
# Путь к базе данных
os.environ["DB_PATH"] = os.path.join(os.environ["APP_DIR"], "database.sqlite")
# Путь к файлу отладки
os.environ["DEBUG_PATH"] = os.path.join(os.environ["APP_DIR"], "debug.log")
# Путь к файлу с данными аккаунта
os.environ["AUTH_PATH"] = os.path.join(os.environ["APP_DIR"], ".auth")
# Путь к директории с персонажами
os.environ["CHARACTERS_PATH"] = os.path.join(os.environ["APP_DIR"], "characters")
# Путь к директории с иконками пользователей
os.environ["USER_ICONS_PATH"] = os.path.join(os.environ["APP_DIR"], "user_icons")
# Путь к директории с иконками интерфейса
os.environ["UI_ICONS_PATH"] = os.path.join(os.environ["APP_DIR"], "ui_icons")
# Путь к директории с иконками предметов
os.environ["ITEMS_PATH"] = os.path.join(os.environ["APP_DIR"], "items")
# Путь к директории с рамками предметов
os.environ["ITEM_BORDERS_PATH"] = os.path.join(os.environ["APP_DIR"], "item_borders")
# Путь к директории с кнопками
os.environ["BUTTONS_PATH"] = os.path.join(os.environ["APP_DIR"], "buttons")
# Путь к директории с локациями
os.environ["LOCATIONS_PATH"] = os.path.join(os.environ["APP_DIR"], "locations")
# Шрифт
if os.path.isfile(font_path := os.path.join(os.environ["APP_DIR"], "font.ttf")):
    os.environ["FONT"] = font_path
# Версия приложения
os.environ["VERSION"] = "0.0.0"
# Сервер
# os.environ["HOST"] = "http://127.0.0.1:5000"  # localhost
os.environ["HOST"] = "https://dungeon-of-masters.herokuapp.com"

pygame.init()

info = pygame.display.Info()
# Разрешение монитора
# TODO: Нужно запретить ставить разрешение больше чем максимально возможное
# TODO: Нужно сделать динамическую генерацию возможных разрешений,
#  в зависимости от разрешения монитора
os.environ["MAX_RESOLUTION"] = f"{info.current_w};{info.current_h}"

logger = __import__("logger").logger
__import__("database").Config.init()
__import__("main").main()

pygame.quit()

logger.info("Клиент закрыт")
