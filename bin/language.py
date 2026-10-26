from pathlib import Path
texts_dir = Path(__file__).resolve().parent.parent / "texts"
lang={}
def load(filename=None):
    global lang
    file_path = texts_dir / f"{filename}.lang"
    lang = {}
    if filename==None or not file_path.exists():
        return lang
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line[:-1]
            if "=" in line:
                key, value = line.split("=", 1)
                lang[key] = value
    return lang


def getword(key,parametrs={}):
    if key in lang:
        text = lang[key]
        parametrs[""] = "\n"
        for key, value in parametrs.items():
            text = text.replace(f"%{key}%",str(value))
    else:
        text = key
        for key, value in parametrs.items():
            text += f"; %{key}% = \"{value}\""
    return text