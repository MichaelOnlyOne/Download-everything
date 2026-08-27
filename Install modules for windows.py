import sys
import subprocess

# Список сторонних библиотек для проверки и установки
REQUIRED_PACKAGES = [
    "yt-dlp",      # Для yt_dlp
    "requests",    # Для requests
    "regex",       # Для regex (re — встроенный, а regex — сторонний)
    "mutagen",     # Для mutagen
    "numpy",       # Для numpy
    "Pillow"       # Для PIL (библиотека называется Pillow)
]

def install_missing_packages():
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

