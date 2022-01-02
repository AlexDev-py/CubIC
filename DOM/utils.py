"""

Функции и классы, которые используются в приложении.

"""


class FinishStatus:
    """
    Статус с которым функция завершила работу.
    """

    close: str = "close"  # Закрытие клиента
    auth_failed: str = "auth_failed"  # Ошибка авторизации
    ok: str = "ok"  # Успешная загрузка

    fail_msg: str = ""  # Текст ошибки

    @classmethod
    def set_msg(cls, msg: str) -> None:
        cls.fail_msg = msg


def check_password(password: str) -> True | False:
    """
    TODO
    Проверка сложности пароля.
    :param password:
    :return: True - пароль подходит
    """
    return True
