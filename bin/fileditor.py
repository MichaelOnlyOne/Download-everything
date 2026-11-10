import music_tag,os,json,mutagen
from . import log,language
#Просто применние метаданных.
def set_audio_tags(filename,info,tracksfolder="."):
    file = music_tag.load_file(os.path.join(tracksfolder,f"{filename}.{info["audioext"]}"))
    file["title"] = info["title"]
    if info.get("artists"):
        file["artist"] = " & ".join(info["artists"])
    else:
        file["artist"] = info["uploader"]
    if info.get("upload_date"):
        file["year"] = int(info["upload_date"][:4])
    if info.get("tags"):
        file["genre"] = ", ".join(info["tags"])
    if info.get("description") and info.get("description") != "":
        file["comment"] = info["description"]
    if info.get("albuminfo"):
        if info["albuminfo"].get("artists"):
            file["albumartist"] = ", ".join(info["albuminfo"]["artists"])
        elif info["albuminfo"].get("uploader"):
            file["albumartist"] = info["albuminfo"]["uploader"]
        if info["albuminfo"].get("add_author_nickname") and file.get("albumartist"):
            info["albuminfo"]["title"] = f"{file["albumartist"]} - {info["albuminfo"]["title"]}"
        if info["albuminfo"].get("title"):
            file["album"] = info["albuminfo"]["title"]
        if isinstance(info["albuminfo"].get("tracks_count"), int):
            file["totaltracks"] = info["albuminfo"]["tracks_count"]
    if isinstance(info.get("trackindex"), int):
        file["trackindex"] = info["trackindex"]
    if info.get("image"):
        file["artwork"] = info["image"]
    file.save()
def set_video_tags(filename,info,tracksfolder="."):
    file = os.path.join(tracksfolder,f"{filename}.{info["videoext"]}")
    if info["videoext"] == "mp4":
        file = mutagen.mp4.MP4(file)
        file["\xa9nam"] = [info["title"]]
        if info.get("artists"):
            file["\xa9ART"] = " & ".join(info["artists"])
        elif info.get("uploader"):
            file["\xa9ART"] = info["uploader"]
        if info.get("upload_date"):
            file["\xa9day"] = [info["upload_date"][:4]]
        if info.get("description"):
            file["desc"] = [info["description"]]
            file["\xa9cmt"] = [info["description"]]
        if info.get("image"):
            file["covr"] = [info["image"]]
        file.save()
    else:
        log.log(language.getword("unknownformat"))
#Применение метаданных из файлов.
def set_tags_from_files(filename,tagstype="audio",infofolder=".",tracksfolder=".",coversfolder="."):
    info = {}
    with open(os.path.join(infofolder,f"{filename}.json"), "r", encoding="ascii") as file:
        info = json.load(file)
    with open(os.path.join(coversfolder,f"{filename}.{info["imagext"]}"), "rb") as image:
        info["image"] = image.read()
    if tagstype == "audio":
        set_audio_tags(filename,info,tracksfolder)
    elif tagstype == "video":
        set_video_tags(filename,info,tracksfolder)
    else:
        log.log(language.getword("invalidvalue",{"key":"tagstype","value":tagstype}))
        pass