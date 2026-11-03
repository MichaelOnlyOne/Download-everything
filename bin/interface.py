from . import fileeditor,downloader,log,language
import os,json


def download_soundcloud_track(url,infofolder=".",tracksfolder=".",coversfolder="."):
    filename = downloader.get_soundcloud_track(url,infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder)
    if not filename is None:
        fileeditor.set_track_tags(filename,infofolder,tracksfolder,coversfolder)

def download_soundcloud_playlist(url,infofolder=".",tracksfolder=".",coversfolder=".",playlistsinfofolder=".",playlistisalbum=False,addauthornickname=False):
    infoname = downloader.download_soundcloud_playlist(url,playlistsinfofolder)
    if infoname is None:
        return
    
    playlistinfo = {}
    with open(os.path.join(playlistsinfofolder,f"{infoname}.json"), "r", encoding="ascii") as file:
        playlistinfo = json.load(file)
    playlistinfo["add_author_nickname"] = addauthornickname
    log.log(language.getword("startingdownloadingalbum",{"title":playlistinfo.get("title")}))
    entries = playlistinfo["entries"]
    del playlistinfo["entries"]
    for index, entry in enumerate(entries):
        log.log(language.getword("progressofdownloadingtracks",{"progress":f"{index+1}/{playlistinfo.get("tracks_count")}","url":entry["url"]}))
        fileeditor.set_track_tags(downloader.get_soundcloud_track(entry["url"],infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder,updateinfo=playlistisalbum,tracknumber=index+1,albuminfo=playlistinfo if playlistisalbum else None),infofolder,tracksfolder,coversfolder)