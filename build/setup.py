"""

    Сборка exe

"""

import re
import shutil

import PyInstaller.__main__

__version__ = "1.0.0-beta.1"

# Изменяем версию в run.py
with open(r"..\DOM\run.py", encoding="utf-8") as file:
    text = file.read()
text = re.sub(
    r'os.environ\["VERSION"] = ".+"', f'os.environ["VERSION"] = "{__version__}"', text
)
with open(r"..\DOM\run.py", "w", encoding="utf-8") as file:
    file.write(text)

# Изменяем версию в установщике
with open("installer.nsi") as file:
    text = file.read()
text = re.sub(
    r'!define PRODUCT_VERSION ".+"', f'!define PRODUCT_VERSION "{__version__}"', text
)
with open("installer.nsi", "w") as file:
    file.write(text)

# Изменяем версию в файле обновления
with open("updater.nsi") as file:
    text = file.read()
text = re.sub(
    r'!define PRODUCT_VERSION ".+"', f'!define PRODUCT_VERSION "{__version__}"', text
)
with open("updater.nsi", "w") as file:
    file.write(text)

# Изменяем версию в version_file
with open(r"sources\version_file") as file:
    text = file.read()
text = re.sub(
    r"StringStruct\(u'(?P<name>(FileVersion)|(ProductVersion))', u'.+'\)",
    rf"StringStruct(u'\g<name>', u'{__version__}')",
    text,
)
with open(r"sources\version_file", "w") as file:
    file.write(text)

PyInstaller.__main__.run(
    [
        "../DOM/run.py",
        "-D",
        "-n=DOM",
        f"--version-file=version_file",
        "--icon=icon.ico",
        "--distpath=.",
        "--workpath=temp",
        "--specpath=sources",
        "-y",
        "--clean",
        # "--onefile",
    ]
)

shutil.rmtree("temp")
