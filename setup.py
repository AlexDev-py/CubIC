"""

    Сборка exe

"""

import re
import shutil

import PyInstaller.__main__

__version__ = "1.0.0-alpha.1"

# Изменяем версию в run.py
with open(r"DOM\run.py", encoding="utf-8") as file:
    text = file.read()
text = re.sub(
    r'os.environ\["VERSION"] = ".+"', f'os.environ["VERSION"] = "{__version__}"', text
)
with open(r"DOM\run.py", "w", encoding="utf-8") as file:
    file.write(text)

# Изменяем версию в установщике
# with open("installer.nsi") as file:
#     text = file.read()
# text = re.sub(
#     r'!define PRODUCT_VERSION ".+"', f'!define PRODUCT_VERSION "{__version__}"', text
# )
# with open("installer.nsi", "w") as file:
#     file.write(text)


PyInstaller.__main__.run(
    [
        "DOM/run.py",
        "-D",
        "-n=DOM",
        f"--version-file=version_file",
        "--icon=icon.ico",
        "--distpath=build",
        "--workpath=build/temp",
        "--specpath=build/sources",
        "-y",
        "--clean",
        # "--onefile",
    ]
)


shutil.rmtree("build/temp")
