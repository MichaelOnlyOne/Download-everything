import json,os,requests,time,yt_dlp
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse
from . import language,log
ErrorSleep=30#Задержка перед повторной попыткой
#Парамтеры для скачивания
class ydl_opts():
    _base = {
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["default", "web_embedded"]
            }
        }
    }
    soundcloud_track = {
        **_base,
        "noplaylist": True,
        "format": "http_mp3_128/hls_mp3_128/hls_opus_64/bestaudio",
        "postprocessors": []
    }
    soundcloud_info = {
        **_base,
        "extract_flat": "in_playlist",
        "skip_download": True,
    }
    youtube_info = {
        **_base,
        "skip_download": True,
    }   
    youtube_cover = {
        **_base,
        "noplaylist": True,
        "extract_flat": False,
    }
    youtube_track = {
        **_base,
        "noplaylist": True,
        "format": "bestaudio/ba/worstaudio",
        "postprocessors": []
    }
    youtube_video = {
        **_base,
        "noplaylist": True,
        "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best"
    }
    rutube_video = {
        **_base,
        "noplaylist": True,
        "format": "bestvideo+bestaudio/best"
    }
    rutube_info = {
        **_base,
        "skip_download": True
    }
    vk_video = {
        **_base,
        "noplaylist": True,
        "format": "best[ext=mp4]/best",
        "format_sort": ["proto:https", "ext:mp4:m4a"]
    }
    vk_info = {
        **_base,
        "noplaylist": True,
        "skip_download": True
    }
def set_ffmpeg_location(path = None):
    if path is None:
        return
    configs = [
        ydl_opts._base,
        ydl_opts.soundcloud_track,
        ydl_opts.soundcloud_info,
        ydl_opts.youtube_info,
        ydl_opts.youtube_cover,
        ydl_opts.youtube_track,
        ydl_opts.youtube_video,
        ydl_opts.rutube_video,
        ydl_opts.rutube_info,
        ydl_opts.vk_video,
        ydl_opts.vk_info
    ]
    for config in configs:
        config["ffmpeg_location"] = path
def set_youtube_cookies(path):
    configs = [
        ydl_opts.youtube_info,
        ydl_opts.youtube_cover,
        ydl_opts.youtube_track,
        ydl_opts.youtube_video
    ]
    
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        for config in configs:
            config["cookiefile"] = path
    else:
        for config in configs:
            config.pop("cookiefile", None)
#Параметры для скачивания конец
#Трек SoundCloud
def get_soundcloud_track(url,infofolder=".", download=True,tracksfolder=".",coversfolder=".",albuminfo=None,updateinfo=False,tracknumber=None):
    if albuminfo is None:
        albuminfo = {"title":"SoundCloud"}
    info = None
    #получение информации
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while info == None:
            log.log(language.getword("obtaininginfo"))
            try:
                info = ydl.extract_info(url, download=False)
                log.log(language.getword("inforeceived"))
            except Exception as Error:
                if "404" in str(Error):
                    log.log(language.getword("404"))
                    
                    return 404
                log.log(language.getword("retrying",{"time":ErrorSleep}))
                time.sleep(ErrorSleep)
    #информация получена её перефращииование
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
    #изображение
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
    del img
    #Трек
    if download:
        trackname = f"{filename}.{info["trackext"]}"
        path = os.path.join(tracksfolder, trackname)
        if os.path.exists(path):
            log.log(language.getword("filealreadyexist",{"file":trackname}))
        else:
            opts = ydl_opts.soundcloud_track.copy()
            opts["outtmpl"] = os.path.join(tracksfolder, f"{filename}.%(ext)s")
            with yt_dlp.YoutubeDL(opts) as ydl:
                while True:
                    log.log(language.getword("downloading",{"file":trackname,"platform":"SoundCloud"}))
                    try:
                        ydl.download([url])
                        log.log(language.getword("filesaved",{"file":trackname}))
                        break
                    except Exception:
                        log.log(language.getword("retrying",{"time":ErrorSleep}))
                        time.sleep(ErrorSleep)
                        
    infoname = f"{filename}.json"
    path = os.path.join(infofolder,infoname)
    if os.path.exists(path) and not updateinfo:
        log.log(language.getword("filealreadyexist",{"file":infoname}))
    else:
        with open(path, "w", encoding="ascii") as file:
            json.dump(info, file, separators=(",", ":"), ensure_ascii=True)
        log.log(language.getword("filecreated",{"file":infoname}))
    return filename
#Плейлист SoundCloud
def download_soundcloud_playlist(url, infofolder=".",UpdateInfo=True):
    info = None
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while not info:
            log.log(language.getword("obtaininginfo"))
            try:
                info = ydl.extract_info(url, download=False)
                log.log(language.getword("inforeceived"))
            except Exception:
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