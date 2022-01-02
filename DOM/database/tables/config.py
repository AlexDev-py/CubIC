import os

from loguru import logger
from sqlite3_api import Table

from ..field_types import Resolution


class Config(Table):
    resolution: Resolution = Resolution(1600, 900)

    @classmethod
    def init(cls) -> None:
        """
        Инициализация конфигурации.
        Создание записи в бд, если не существует.
        Добавление в виртуальное окружение.
        """
        logger.trace("Инициализация конфигурации")
        db = cls(os.environ["DB_PATH"])
        config = db.filter()
        if not config:
            logger.debug("Конфигурация не установлена")
            db.insert()
            config = db.filter()
        elif isinstance(config, list):
            logger.warning("В таблице конфигурации больше одной записи")
            db.api.execute("DROP TABLE config")
            db.insert()
            config = db.filter()

        config.add_to_env()

    def add_to_env(self) -> None:
        """
        Добавление конфигурации в виртуальное окружение.
        """
        logger.trace("Добавление конфигурации в виртуальное окружение")
        for field in self.get_fields():
            os.environ[field] = str(self.__dict__[field])

    @classmethod
    def update(cls, **fields: [str, ...]) -> None:
        """
        Дополняет стандартную функцию.
        Обновляет данные как в бд, так и в виртуальном окружении.
        """
        logger.opt(colors=True).debug(
            "Обновление конфигурации. "
            + ", ".join((f"<le>{k}</le>=<y>{v}</y>" for k, v in fields.items()))
        )
        config = cls(os.environ["DB_PATH"]).filter()
        super(Config, config).update(**fields)
        config.add_to_env()
