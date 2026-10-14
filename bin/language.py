from pathlib import Path
bin_dir = Path(__file__).resolve().parent
texts_dir = bin_dir.parent / "texts"
languages_dict = {}
for file_path in texts_dir.glob("*.lang"):
    file_translations = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                file_translations[key.strip()] = value.strip()
    lang_name = file_path.stem 
    languages_dict[lang_name] = file_translations
def getword(key, lang="ru_RU"):
    if lang in languages_dict and key in languages_dict[lang]:
        return languages_dict[lang][key]
    return key