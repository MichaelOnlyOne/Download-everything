import datetime
from pathlib import Path
def log(message):
    print(message)
    Path(__file__).resolve().parent.parent.joinpath("log.txt").open("a", encoding="utf-8").write(f"[{datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')}] {message}\n")