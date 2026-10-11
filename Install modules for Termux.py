import sys
import subprocess
import os

REQUIRED_PACKAGES = [
    "yt-dlp",
    "requests",
    "regex",
    "mutagen",
    "numpy",
    "Pillow"
]

def install_missing_packages():
    os.environ["MATHLIB"] = "m"
    
    for package in REQUIRED_PACKAGES:
        import_name = "PIL" if package == "Pillow" else package
        try:
            __import__(import_name)
        except ImportError:
            print(f"Библиотека {package} не найдена. Установка...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Успешно установлено: {package}\n")
            except subprocess.CalledProcessError:
                print(f"Ошибка при установке {package}. Проверьте подключение к сети.")
install_missing_packages()
