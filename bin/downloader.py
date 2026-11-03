import json,os,requests,time,yt_dlp
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse
from . import language,log
ErrorSleep=30#Задержка перед повторной попыткой.
#Парамтеры для скачивания.
class ydl_opts():
    base = {
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {
                "formats": ["missing_pot"]
            }
        }
    }
    listformats = {
        **base,
        "listformats": True
    }
    soundcloud_track = {
        **base,
        "noplaylist": True,
        "format": "http_mp3_128/hls_mp3_128/hls_opus_64/bestaudio"
    }
    soundcloud_info = {
        **base,
        "extract_flat": "in_playlist",
        "skip_download": True,
    }
    youtube_info = {
        **base,
        "skip_download": True,
    }
    youtube_music_track = {
        **base,
        "noplaylist": True,
        "format": "bestaudio/best"
    }
    youtube_video = {
        **base,
        "noplaylist": True,
        "format": "bestvideo+bestaudio/best"
    }
    youtube_listformats = {
        **listformats
    }
    rutube_video = {
        **base,
        "noplaylist": True,
        "format": "bestvideo+bestaudio/best"
    }
    rutube_info = {
        **rutube_video,
        "skip_download": True
    }
    vk_video = {
        **base,
        "noplaylist": True,
        "format": "best[ext=mp4]/best",
        "format_sort": ["proto:https", "ext:mp4:m4a"]
    }
    vk_info = {
        **vk_video,
        "skip_download": True
    }

ydl_opts_names = [name for name in vars(ydl_opts) if not name.startswith('_')]
def set_ffmpeg_location(path = None):
    if path is None:
        return
    for opt in ydl_opts_names:
        getattr(ydl_opts,opt)["ffmpeg_location"] = path
def set_youtube_clients(clients=["default"]):
    if isinstance(clients, str):
        clients = [clients]
    if "default" not in clients:
        clients += ["default"]
    for opt in ydl_opts_names:
        getattr(ydl_opts,opt)["extractor_args"]["youtube"]["player_client"] = clients
def set_youtube_cookies(path=""):
    yt_opts_names = ["youtube_info","youtube_music_track","youtube_video","youtube_listformats"]
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        #Если куки нет.
        for opt in ydl_opts_names:
            getattr(ydl_opts,opt)["cookiefile"] = path
    else:
        #Если куки есть.
        for opt in ydl_opts_names:
            getattr(ydl_opts,opt).pop("cookiefile", None)
#Параметры для скачивания конец.
#Трек SoundCloud.
def get_soundcloud_track(url,infofolder=".",download=True,tracksfolder=".",coversfolder=".",albuminfo=None,updateinfo=False,tracknumber=None):
    if albuminfo is None:
        albuminfo = {"title":"SoundCloud"}
    info = None
    #Получение информации и скачивание.
    opts = ydl_opts.soundcloud_track.copy()
    opts["outtmpl"] = os.path.join(tracksfolder, ".TEMP.%(ext)s")
    with yt_dlp.YoutubeDL(opts) as ydl:
        while info == None:
            log.log(language.getword("obtaininginfoanddownloading"))
            try:
                info = ydl.extract_info(url,download=download)
                log.log(language.getword("inforeceived"))
            except Exception as Error:
                if "403" not in str(Error) and "429" not in str(Error):
                    log.log(language.getword("error"))
                    return None
                log.log(language.getword("retrying",{"time":ErrorSleep}))
                time.sleep(ErrorSleep)
    #Информация получена, её пеоеформатирование.
    normal_url = info.get("webpage_url", url)
    path_parts = [p for p in urlparse(normal_url).path.split("/") if p]
    info = {
        "title":info.get("title"),
        "artists":info.get("artists"),
        "uploader":info.get("uploader"),
        "trackext":info.get("audio_ext"),
        "albuminfo":albuminfo,
        "description":info.get("description"),
        "license":info.get("license"),
        "thumbnail":info.get("thumbnail"),
        "tags":info.get("tags"),
        "upload_date":info.get("upload_date"),
        "duration":info.get("duration"),
        "authorfromurl":path_parts[-2],
        "titlefromurl":path_parts[-1].split("?")[0]
    }
    if isinstance(tracknumber, int):
        info["tracknumber"] = tracknumber
    del normal_url,path_parts
    filename = f"{info["authorfromurl"]} {info["titlefromurl"]}"
    
    infopath = os.path.join(infofolder,f"{filename}.json")
    #Перемещение трека
    if download:
        os.replace(os.path.join(tracksfolder, f".TEMP.{info['trackext']}"),os.path.join(tracksfolder, f"{filename}.{info['trackext']}"))
    #изображение
    if download or not os.path.exists(infopath):
        response = None
        log.log(language.getword("linktoimage",{"link":info["thumbnail"]}))
        while not response:
            log.log(language.getword("obtaininginfo"))
            try:
                response = requests.get(info["thumbnail"])
                log.log(language.getword("inforeceived"))
            except Exception:
                log.log(language.getword("retrying",{"time":ErrorSleep}))
                time.sleep(ErrorSleep)
        img = Image.open(BytesIO(response.content))
        del response
        info["thumbnailext"] = os.path.splitext(urlparse(info["thumbnail"]).path)[1].lstrip(".").lower()
        info["thumbnailformat"] = img.format
        if download:
            covername=f"{filename}.{info["thumbnailext"]}"
            path = os.path.join(coversfolder,covername)
            if os.path.exists(path):
                log.log(language.getword("filealreadyexist",{"file":covername}))
            else:
                img = img.convert("RGB")
                img.save(path,info["thumbnailformat"])
                log.log(language.getword("filesaved",{"file":covername}))
    
    #Сохранения json с данными
    if os.path.exists(infopath) and not updateinfo and download:
        log.log(language.getword("filealreadyexist",{"file":filename+".json"}))
    else:
        with open(infopath, "w", encoding="ascii") as file:
            json.dump(info, file, separators=(",", ":"), ensure_ascii=True)
        log.log(language.getword("filecreated",{"file":filename+".json"}))
    return filename
#Плейлист SoundCloud.
def download_soundcloud_playlist(url, infofolder=".",UpdateInfo=True):
    info = None
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while not info:
            log.log(language.getword("obtaininginfo"))
            try:
                info = ydl.extract_info(url, download=False)
                log.log(language.getword("inforeceived"))
            except Exception as Error:
                if "403" not in str(Error) and "429" not in str(Error):
                    log.log(language.getword("error"))
                    return None
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    entries = []
    for entry in info["entries"]:
        entries.append({
            "url":entry.get("url")
        })
    info = {
        "title":info.get("title"),
        "artists":info.get("album_artists"),
        "uploader":info.get("uploader"),
        "entries":entries,
        "description":info.get("description"),
        "license":info.get("license"),
        "tags":info.get("tags"),
        "tracks_count":info.get("playlist_count"),
        "upload_date":info.get("upload_date"),
        "id":info.get("id")
    }
    infoname = f"{info["id"]}.json"
    path = os.path.join(infofolder,infoname)
    if os.path.exists(path) and not UpdateInfo:
        log.log(language.getword("filealreadyexist",{"file":infoname}))
    else:
        with open(path, "w", encoding="ascii") as file:
            json.dump(info, file, separators=(",", ":"), ensure_ascii=True)
        log.log(language.getword("filecreated",{"file":infoname}))
    return info["id"]

#Видео ВКонтакте
#Видео RuTube
