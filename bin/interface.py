from . import fileditor,downloader,log,language
import os,json


def download_soundcloud_track(url,infofolder=".",tracksfolder=".",coversfolder=".",nosavemode=True):
    filename, info = downloader.get_soundcloud_track(url,infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder,nosavemode=nosavemode)
    if filename is None:
        return
    if nosavemode:
        fileditor.set_audio_tags(filename,info,tracksfolder)
    else:
        filename = downloader.get_soundcloud_track(url,infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder,nosavemode=nosavemode)
        if not filename is None:
            fileditor.set_tags_from_files(filename,"audio",infofolder,tracksfolder,coversfolder)

def download_soundcloud_playlist(url,infofolder=".",tracksfolder=".",coversfolder=".",playlistsinfofolder=".",playlistisalbum=False,addauthornickname=False,nosavemode=True):
    playlistinfo = {}
    if nosavemode:
        playlistinfo = downloader.download_soundcloud_playlist(url,playlistsinfofolder,nosavemode=nosavemode)
    else:
        infoname = downloader.download_soundcloud_playlist(url,playlistsinfofolder,nosavemode=nosavemode)
        if infoname is None:
            return
        with open(os.path.join(playlistsinfofolder,f"{infoname}.json"), "r", encoding="ascii") as file:
            playlistinfo = json.load(file)
    playlistinfo["add_author_nickname"] = addauthornickname
    log.log(language.getword("startingdownloadingalbum",{"title":playlistinfo.get("title")}))
    entries = playlistinfo["entries"]
    del playlistinfo["entries"]
    for index, entry in enumerate(entries):
        log.log(language.getword("progressofdownloadingtracks",{"progress":f"{index+1}/{playlistinfo.get("tracks_count")}","url":entry["url"]}))
        filename,info = downloader.get_soundcloud_track(entry["url"],infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder,update=playlistisalbum,trackindex=index+1,albuminfo=playlistinfo if playlistisalbum else None,nosavemode=nosavemode)
        if filename is None:
            continue
        if nosavemode:
            fileditor.set_audio_tags(filename,info,tracksfolder)
        else:
            fileditor.set_tags_from_files(filename,"audio",infofolder,tracksfolder,coversfolder)
def download_vk_video(url,infofolder=".",tracksfolder=".",coversfolder=".",nosavemode=True):
    filename,info = downloader.get_vk_video(url,infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder,nosavemode=nosavemode)
    if filename is None:
        return
    if nosavemode:
        fileditor.set_video_tags(filename,info)
    else:
        if not filename is None:
            fileditor.set_tags_from_files(filename,"video",infofolder,tracksfolder,coversfolder)