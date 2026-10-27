import music_tag,os,json
from . import log
def set_track_tags(filename,infofolder=".",tracksfolder=".",coversfolder="."):
    info = {}
    with open(os.path.join(infofolder,f"{filename}.json"), "r", encoding="ascii") as file:
        info = json.load(file)
    file = music_tag.load_file(os.path.join(tracksfolder,f"{filename}.{info["trackext"]}"))
    file["title"] = info["title"]
    if info["artists"]:
        file["artist"] = " & ".join(info["artists"])
    else:
        file["artist"] = info["uploader"]
    if info.get("upload_date"):
        file["year"] = int(info["upload_date"][:4])
    if info.get("tags"):
        file["genre"] = ", ".join(info["tags"])
    if info.get("description"):
        file["comment"] = info["description"]
    if info.get("albuminfo"):
        if info["albuminfo"].get("artists"):
            file["albumartist"] = " & ".join(info["albuminfo"]["artists"])
        elif info["albuminfo"].get("uploader"):
            file["albumartist"] = info["albuminfo"]["uploader"]
        if info["albuminfo"].get("add_author_nickname") and file.get("albumartist"):
            info["albuminfo"]["title"] = f"{file["albumartist"]} - {info["albuminfo"]["title"]}"
        if info["albuminfo"].get("title"):
            file["album"] = info["albuminfo"]["title"]
        if isinstance(info["albuminfo"].get("tracks_count"), int):
            file["totaltracks"] = info["albuminfo"]["tracks_count"]
    if isinstance(info.get("tracknumber"), int):
        file["tracknumber"] = info["tracknumber"]
    with open(os.path.join(coversfolder,f"{filename}.{info["thumbnailext"]}"), "rb") as img:
        file["artwork"] = img.read()
    file.save()