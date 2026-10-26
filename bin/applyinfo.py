import music_tag,os,json

def set_track_tags(filename,infofolder=".",tracksfolder=".",coversfolder="."):
    info = {}
    with open(os.path.join(infofolder,f"{filename}.json"), "r", encoding="ascii") as file:
        info = json.load(file)
    file = music_tag.load_file(os.path.join(tracksfolder,f"{filename}.{info["trackext"]}"))
    file['title'] = info["title"]
    file['artist'] = " & ".join(info["artists"])
    if "upload_date" in info:
        file['year'] = int(info["upload_date"][:4])
    if "tags" in info:
        file['genre'] = ", ".join(info['tags'])
    if description in info:
        file['comment'] = info['description']
    if "albuminfo" in data:
        if "title" in info["albuminfo"]:
            file['album'] = info["albuminfo"]["title"]
        if "artists" in info["albuminfo"]:
            file['albumartist'] = ", ".join(info["albuminfo"]["artists"])
        if "tracks_count" in info["albuminfo"]:
            file['totaltracks'] = info["albuminfo"]["tracks_count"]
    if "tracknumber" in info:
        file['tracknumber'] = info["tracknumber"]
    with open(os.path.join(coversfolder,f"{filename}.{info["thumbnailext"]}"), "rb") as img:
        file['artwork'] = img.read()
    file.save()