from . import fileeditor,downloader,log,language
import os,json
def download_soundcloud_track(url,infofolder=".",tracksfolder=".",coversfolder="."):
    fileeditor.set_track_tags(downloader.get_soundcloud_track(url,infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder),infofolder,tracksfolder,coversfolder)
def download_soundcloud_playlist(url,infofolder=".",tracksfolder=".",coversfolder=".",playlistsinfofolder=".",playlistisalbum=False,addauthornickname=False):
    infoname = downloader.download_soundcloud_playlist(url,playlistsinfofolder)
    playlistinfo = {}
    with open(os.path.join(playlistsinfofolder,f"{infoname}.json"), "r", encoding="ascii") as file:
        playlistinfo = json.load(file)
    playlistinfo["add_author_nickname"] = addauthornickname
    log.log(language.getword("startingdowloadingalbum",{"title":playlistinfo.get("title")}))
    for index, entry in enumerate(playlistinfo["entries"]):
        log.log(language.getword("progressofdowloadingplaylist",{"progress":f"{index+1}/{playlistinfo.get("tracks_count")}","url":entry["url"]}))
        fileeditor.set_track_tags(downloader.get_soundcloud_track(entry["url"],infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder,updateinfo=playlistisalbum,tracknumber=index+1,albuminfo=playlistinfo if playlistisalbum else None),infofolder,tracksfolder,coversfolder)