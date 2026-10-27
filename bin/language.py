import pathlib,json
texts_dir = pathlib.Path(__file__).resolve().parent.parent / "texts"
lang={}
def load(filename=None):
    global lang
    file_path = texts_dir / f"{filename}.lang"
    lang = {}
    if filename==None or not file_path.exists():
        return lang
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.replace("\n","")
            if "=" in line:
                key, value = line.split("=", 1)
                lang[key] = value
    return lang
def getlangs():
    lang_files = [file.name[:-5] for file in texts_dir.glob("*.lang")]
    return lang_files
def getword(key,parametrs=None):
    parametrs = {} if parametrs is None else parametrs
    if key in lang:
        text = lang[key]
        parametrs[""] = "\n"
        for key, value in parametrs.items():
            text = text.replace(f"%{key}%",str(value))
    else:
        text = key
        for key, value in parametrs.items():
            text += f"; %{key}% = {json.dumps(value,ensure_ascii=False)}"
    return text