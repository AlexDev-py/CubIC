import os

from .tables.config import Config

Config(os.environ["DB_PATH"]).create_table()

__all__ = ["Config"]
