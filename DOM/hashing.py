import hashlib


def get_hash(file_path: str, hash_func=hashlib.md5) -> str:
    """
    :param file_path: Путь к файлу.
    :param hash_func: Хэш функция.
    :return: Хэш файла.
    """
    with open(file_path, "rb") as f:
        img_hash = hash_func()
        # Читаем файл частями
        while chunk := f.read(8192):
            img_hash.update(chunk)
    return img_hash.hexdigest()
