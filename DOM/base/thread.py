"""

Менеджер дополнительного потока.
Дает интерфейс для выполнения функций в отдельном потоке.

Существует, для того, чтобы окно приложения не зависало,
при выполнении ресурса затратных задач,

"""

from __future__ import annotations

import re
import threading
import time
import typing as ty

from loguru import logger

if ty.TYPE_CHECKING:
    from .types import Response


def _safe_text(text: str) -> str:
    if isinstance(text, str):
        return re.sub(r"<(?P<obj>.*)>", r"\<\g<obj>>", text)
    return text


class Thread:
    _thread: threading.Thread = ...  # Объект потока
    _workers: list[Thread] = []  # Список заданий
    _running: True | False = False  # True - поток активен
    _sleeping = 1  # Интервал проверки новых заданий (в секундах)

    def __new__(cls, *args, **kwargs):
        """
        Создание нового экземпляра класса.
        """
        if cls._thread is ...:  # Если поток не создан
            cls._running = True
            cls._thread = threading.Thread(target=cls._worker, name="ThreadWorker")
            # Поток автоматически остановится при остановке основного потока
            cls._thread.daemon = True
            cls._thread.start()
            logger.opt(colors=True).debug(f"Поток <c>{cls._thread.name}</c> запущен")

        return super(Thread, cls).__new__(cls)

    def __init__(
        self,
        worker: ty.Callable[[...], Response],
        *,
        args: tuple[...] = (),
        kwargs: dict[str, ...] = None,
        callback: ty.Callable[[Response], ty.Any] = None,
        repetitive: True | False = False,
        timeout: int = 1,
    ):
        """
        Менеджер дополнительного потока.

        :param worker: Функция, которую нужно выполнить.
        :type worker: Функция(может быть lambda), принимающая любое число аргументов
         и возвращающая любое значение.
        :param args: Позиционные аргументы, которые передадутся в выполняемую функцию.
        :param kwargs: Именованные аргументы, которые передадутся в выполняемую функцию.
        :param callback: Функция, которая будет вызвана,
         после завершения работы основной функции.
        :type callback: Функция принимающая строго 1 позиционный аргумент
         и возвращающая любое значение.
        :param repetitive: True - Задание будет повторяться каждые <timeout> секунд.
        :param timeout: Раз в сколько секунд будет выполняться задание.
        """
        logger.opt(colors=True).trace(
            "Создано новое задание "
            "<y>worker</y>=<c>{worker}</c> "
            "<y>args</y>=<c>{args}</c> "
            "<y>kwargs</y>=<c>{kwargs}</c> "
            "<y>callback</y>=<c>{callback}</c> "
            "<y>repetitive</y>=<c>{repetitive}</c>",
            worker=str(worker),
            args=args,
            kwargs=kwargs,
            callback=str(callback),
            repetitive=repetitive,
        )
        self.worker = worker
        self.args = args
        self.kwargs = kwargs or {}
        self.callback = callback
        self.repetitive = repetitive
        self.timeout = timeout

        self._last_start = 0

    @classmethod
    def _worker(cls) -> ty.NoReturn:
        # Основной цикл потока.
        while cls._running:
            for worker in cls._workers.copy():
                if worker.repetitive:
                    if worker._last_start + worker.timeout > int(time.time()):
                        continue
                try:
                    response = worker.worker(*worker.args, **worker.kwargs)
                    if worker.callback:
                        worker.callback(response)
                except Exception:
                    import traceback

                    traceback.print_exc()

                if not worker.repetitive:
                    cls._workers.remove(worker)
                    logger.opt(colors=True).trace(
                        "Задание <c>{worker}</c> выполнено", worker=worker.worker
                    )
                else:
                    worker._last_start = int(time.time())
            time.sleep(cls._sleeping)

    def run(self) -> None:
        """
        Запускает задания.
        """
        self.__class__._workers.append(self)
        logger.opt(colors=True).trace(
            "Задание <c>{worker}</c> добавлено в очередь", worker=self.worker
        )
