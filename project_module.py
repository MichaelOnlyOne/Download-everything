import os
import time
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image
import yt_dlp
import requests
import re
import regex
import mutagen
import numpy
import shutil
import glob
#Базовые перемменые которые можно редактировать
ErrorSleep = 30 #Задержка перед повторной попыткой при ошибке
#Доп функции
def log(tag,text,spacecount = 0,crop=False):
    if spacecount == 0:
        spacecount = len(tag)
    if len(tag) > spacecount and crop:
        tag = tag[:spacecount]
    elif (spacecount - len(tag))%2 == 1:
        tag += " "
    print(f"[{" "*((spacecount - len(tag))//2)}{tag}{" "*((spacecount - len(tag))//2)}] {text}")
def write_if_empty(file_path, text):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
def read_links_from_file(file_path):
    links = []
    if not os.path.exists(file_path):
        log("links from file", f"Ошибка: Файл не найден: {file_path}")
        return links

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            
            if not clean_line or clean_line.startswith('#'):
                continue
                
            if ' #' in clean_line:
                clean_line = clean_line.split(' #')[0].strip()
            elif '#' in clean_line and not clean_line.startswith('http'):
                clean_line = clean_line.split('#')[0].strip()
                
            if clean_line:
                links.append(clean_line)
                
    return links
def inputnumber(a,b=None):
    if b == None:
        b,a = a,1
    while True:
        inp = input("> ")
        if not inp.isdigit():
            print("Введи натуральное число")
            continue
        val = int(inp)
        if val not in range(a, b+1): 
            print(f"Введи число в диапазоне {a}-{b}")
            continue
        return val
def makesafename(safe_name):
    safe_name = safe_name.replace('/', '-').replace('\\', '-').replace(':', ' -')
    safe_name = regex.sub(r'[^\p{L}\p{N}\s\-\_ \(\)\[\]]', '', safe_name)
    safe_name = regex.sub(r'\s+', ' ', safe_name).strip()
    if len(safe_name) > 100:
        safe_name = safe_name[:100].strip()
        
    return safe_name
def input_album_parametrs():
    params = {"AddNumberAtStartOfTheName":False,
    "PlaylistnameIsAlbum":True,
    "MakeAlbumNameUniqueByAddingPlatformNameAtTheEnd":True,
    "AddIndexAttheStartOfFilesNames":False,
    "AddAuthorNameAtTheStart":False,
    "AddPlatformNameAndIdToAlbumName":False,
    "SaveToFolder":False,
    }
    #Это можно назвать мини опросом...
    print("Использовать название плейлиста как альбом")
    print("(если плеер не имеет функции плейлистов")
    print("или плейлист это реально альбом)")
    print("[1] - Да\n[2] - Нет")
    params["PlaylistnameIsAlbum"] = inputnumber(2) == 1
    if not params["PlaylistnameIsAlbum"]:
        return params
    print("Добавить в название альбома название платформы и айди плейлиста?")
    print("[1] - Да\n[2] - Нет")
    params["AddPlatformNameAndIdToAlbumName"] = inputnumber(2) == 1
    print("Добавить в название альбома никнейм автора?")
    print("[1] - Да\n[2] - Нет")
    params["AddAuthorNameAtTheStart"] = inputnumber(2) == 1
    print("Добавлять нумерацию в начале имени (да если её нет)?")
    print("[1] - Да\n[2] - Нет")
    params["AddIndexAttheStartOfSongsNames"] = inputnumber(2) == 1
    print("Создавать отдельную папку под плейлист/альбом?")
    print("[1] - Да\n[2] - Нет")
    params["SaveToFolder"] = inputnumber(2) == 1
    if params["SaveToFolder"]:
        print("Добавлять нумерацию в начале названий файлов?")#почти бесполезная функция
        print("[1] - Да\n[2] - Нет")
        params["AddIndexAttheStartOfFilesNames"] = inputnumber(2) == 1
    return params
def _get_abs_or_rel(path, base):
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(base, path))
#Создание файлов и папок

class dirs_paths():
    __base_dir__ = os.path.dirname(os.path.abspath(__file__))
    
    bin = os.path.join(__base_dir__, '.bin')
    confs = os.path.join(__base_dir__, '.conf')
    inputs = os.path.join(__base_dir__, 'Input Files')
    cookies = os.path.join(__base_dir__, 'Cookies')
    for path in [bin, confs, inputs]:
        if not os.path.exists(path):
            os.makedirs(path)

class files_paths():
    SoundCloud_Music_dir_conf = os.path.join(dirs_paths.confs, "SoundCloud Music Storage.txt")
    Youtube_Music_dir_conf = os.path.join(dirs_paths.confs, "Youtube Music Storage.txt")
    Video_Path_Conf = os.path.join(dirs_paths.confs, "Video Save Path.txt")
    Music_Path_Conf = os.path.join(dirs_paths.confs, "Music Save Path.txt")
    Cover_Path_Conf = os.path.join(dirs_paths.confs, "Cover Save Path.txt")
    Playlist_Path_Conf = os.path.join(dirs_paths.confs, "Playlist Save Path.txt")
    ffmpeg_Path_Conf = os.path.join(dirs_paths.confs, "ffmpeg Path.txt")
    SoundCloud_Playlists_links = os.path.join(dirs_paths.inputs, "SoundCloud Playlists links.txt")
    Youtube_Music_Playlists_links = os.path.join(dirs_paths.inputs, "Youtube Music Playlists links.txt")
    Youtube_Music_links = os.path.join(dirs_paths.inputs, "Youtube Music links.txt")
    Youtube_Videos_links = os.path.join(dirs_paths.inputs, "Youtube Videos links.txt")
    Rutube_Videos_links = os.path.join(dirs_paths.inputs, "Rutube Videos links.txt")
    Youtube_cookies = os.path.join(dirs_paths.cookies, "Youtube.txt")
    log = os.path.join(dirs_paths.__base_dir__, "log.txt")

write_if_empty(files_paths.SoundCloud_Music_dir_conf, "Music/SoundCloud")
write_if_empty(files_paths.Youtube_Music_dir_conf, "Music/Youtube")
write_if_empty(files_paths.Video_Path_Conf, "Videos")
write_if_empty(files_paths.Music_Path_Conf, "Music")
write_if_empty(files_paths.Cover_Path_Conf, "Covers")
write_if_empty(files_paths.Playlist_Path_Conf, "Playlists")
write_if_empty(files_paths.ffmpeg_Path_Conf, '.bin')

with open(files_paths.Video_Path_Conf, 'r', encoding='utf-8') as f:
    dirs_paths.Videos = _get_abs_or_rel(f.read().strip(), dirs_paths.__base_dir__)

with open(files_paths.Music_Path_Conf, 'r', encoding='utf-8') as f:
    dirs_paths.Music = _get_abs_or_rel(f.read().strip(), dirs_paths.__base_dir__)

with open(files_paths.Cover_Path_Conf, 'r', encoding='utf-8') as f:
    dirs_paths.Covers = _get_abs_or_rel(f.read().strip(), dirs_paths.__base_dir__)

with open(files_paths.Playlist_Path_Conf, 'r', encoding='utf-8') as f:
    dirs_paths.Playlists = _get_abs_or_rel(f.read().strip(), dirs_paths.__base_dir__)

with open(files_paths.ffmpeg_Path_Conf, 'r', encoding='utf-8') as f:
    dirs_paths.bin = _get_abs_or_rel(f.read().strip(), dirs_paths.__base_dir__)

dirs_paths.Youtube_Covers = os.path.join(dirs_paths.Covers, "Youtube")
dirs_paths.YoutubeMusic_Covers = os.path.join(dirs_paths.Covers, "YoutubeMusic")
dirs_paths.SoundCloud_Covers = os.path.join(dirs_paths.Covers, "SoundCloud")
dirs_paths.Rutube_Videos = os.path.join(dirs_paths.Videos, "Rutube")
dirs_paths.Youtube_Videos = os.path.join(dirs_paths.Videos, "Youtube")
dirs_paths.VK_Videos = os.path.join(dirs_paths.Videos, "VK")
dirs_paths.Youtube_Music = os.path.join(dirs_paths.Music, "Youtube")
dirs_paths.SoundCloud_Music = os.path.join(dirs_paths.Music, "SoundCloud")
dirs_paths.SoundCloud_Playlists = os.path.join(dirs_paths.Playlists, "SoundCloud")
dirs_paths.Youtube_Playlists = os.path.join(dirs_paths.Playlists, "Youtube")

for attr in dir(dirs_paths):
    if not attr.startswith('__'):
        folder_path = getattr(dirs_paths, attr)
        if isinstance(folder_path, str) and not os.path.exists(folder_path):
            os.makedirs(folder_path)

write_if_empty(files_paths.SoundCloud_Playlists_links, "# Вставьте сюда ссылки на плейлисты SoundCloud\n")
write_if_empty(files_paths.Youtube_Music_Playlists_links, "# Вставьте сюда ссылки на плейлисты Youtube Music\n")
write_if_empty(files_paths.Youtube_Music_links, "# Вставьте сюда ссылки на треки Youtube Music\n")
write_if_empty(files_paths.Youtube_Videos_links, "# Вставьте сюда ссылки на видео Youtube\n")
write_if_empty(files_paths.Rutube_Videos_links, "# Вставьте сюда ссылки на видео Rutube\n")
write_if_empty(files_paths.log, "")
write_if_empty(files_paths.Youtube_cookies, '')
#Входы в аккаунты
#Парамептры для модуля - yt_dlp
class ydl_opts():
    _base = {
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': dirs_paths.bin,
        'extractor_args': {
            'youtube': {
                'player_client': ['default', 'web_embedded']
            }
        }
    }
    _youtube_cookie = {'cookiefile': files_paths.Youtube_cookies} if os.path.exists(files_paths.Youtube_cookies) and os.path.getsize(files_paths.Youtube_cookies) > 0 else {}

    soundcloud_info = {
        **_base,
        'extract_flat': 'in_playlist',
        'skip_download': True,
    }
    youtube_info = {
        **_base,
        **_youtube_cookie,
        'skip_download': True,
    }   
    youtube_cover = {
        **_base,
        **_youtube_cookie,
        'noplaylist': True,
        'extract_flat': False,
    }

    soundcloud_audio_track = {
        **_base,
        'noplaylist': True,
        'format': 'http_mp3_128/hls_mp3_128/hls_opus_64/bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    soundcloud_audio_playlist = {
        **_base,
        'noplaylist': False,
        'format': 'http_mp3_128/hls_mp3_128/hls_opus_64/bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    youtube_audio_track = {
        **_base,
        **_youtube_cookie,
        'noplaylist': True,
        'format': 'bestaudio/ba/worstaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    youtube_video_track = {
        **_base,
        **_youtube_cookie,
        'noplaylist': True,
        'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best',
    }
    rutube_video_track = {
        **_base,
        'noplaylist': True,
        'format': 'bestvideo+bestaudio/best',
    }
    rutube_info = {
        **_base,
        'skip_download': True,
    }
    vk_video_track = {
        **_base,
        'noplaylist': True,
        'format': 'best[ext=mp4]/best',
        'format_sort': ['proto:https', 'ext:mp4:m4a'],
    }

    vk_info = {
        **_base,
        'noplaylist': True,
        'skip_download': True,
    }
#Сылки в имена
class url_to_name:
    log_tag = "url to name"

    @staticmethod
    def youtube_video(url):
        with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'Untitled Video')
                    v_id = info.get('id', 'unknown_id')
                    return f"{makesafename(video_title)} [{v_id}]"
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def youtube_track(url):
        track_opts = ydl_opts.youtube_info.copy()
        track_opts['noplaylist'] = True
        with yt_dlp.YoutubeDL(track_opts) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    v_id = info.get('webpage_url_id') or info.get('display_id') or info.get('id')
                    if not v_id or len(v_id) > 20:
                        v_id = 'unknown_id'
                    raw_username = (
                        info.get('uploader_id') or 
                        info.get('channel_id') or 
                        'unknown_author'
                    )
                    if not raw_username or str(raw_username).strip().lower() == 'none':
                        username = f"channel_{v_id}"
                    else:
                        username = str(raw_username)
                        if username.startswith('@'):
                            username = username[1:]       
                    result = makesafename(f"{username} {v_id}")
                    return result
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def rutube_video(url):
        with yt_dlp.YoutubeDL(ydl_opts.rutube_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    video_id = info.get('id', 'unknown_id')
                    video_title = info.get('title', 'Untitled Video')
                    return f"{makesafename(video_title)} [{video_id}]"
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def vk_video(url):
        with yt_dlp.YoutubeDL(ydl_opts.vk_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    video_id = info.get('id', 'unknown_id')
                    video_title = info.get('title', 'Untitled Video')
                    return f"{makesafename(video_title)} [{video_id}]"
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def soundcloud_track(url):
        with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    normal_url = info.get('webpage_url', url)
                    path_parts = [p for p in urlparse(normal_url).path.split('/') if p]
                    artist_slug = path_parts[-2] if len(path_parts) >= 2 else "artist"
                    track_slug = path_parts[-1].split('?')[0] if path_parts else "track"
                    return makesafename(f"{artist_slug} {track_slug}")
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def soundcloud_playlist_folder(url):
        with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    playlist_title = info.get('title', 'Untitled Playlist')
                    playlist_id = str(info.get('id', 'unknown_id'))
                    if ":" in playlist_id:
                        match = re.search(r'\b\d{5,}\b', playlist_id)
                        if match:
                            playlist_id = match.group(0)
                        else:
                            playlist_id = playlist_id.replace(':', '-')
                    return f"{playlist_id} {makesafename(playlist_title)}"
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def youtube_playlist_folder(url):
        with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    playlist_title = info.get('title', 'Untitled Playlist')
                    playlist_id = info.get('id', 'unknown_id')
                    return makesafename(f"{playlist_title} {playlist_id}")
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def soundcloud_playlist_for_info(url,AuthorMark=False,PlatformMark=False):
        with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    playlist_title = info.get('title', 'Untitled Playlist')
                    playlist_id = str(info.get('id', 'unknown_id'))
                    author_name = info.get('uploader', 'Unknown Author')
                    if ":" in playlist_id:
                        match = re.search(r'\b\d{5,}\b', playlist_id)
                        if match:
                            playlist_id = match.group(0)
                        else:
                            playlist_id = playlist_id.replace(':', '-')
                    out = playlist_title
                    if AuthorMark:
                        out = f"{author_name} - {out}"
                    if PlatformMark:
                        out = f"{out} (SoundCloud: {playlist_id})"
                    return out
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)

    @staticmethod
    def youtube_playlist_for_info(url,AuthorMark=False,PlatformMark=False):
        with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
            while True:
                try:
                    info = ydl.extract_info(url, download=False)
                    playlist_title = info.get('title', 'Untitled Playlist')
                    playlist_id = info.get('id', 'unknown_id')
                    author_name = info.get('uploader', 'Unknown Author')
                    out = playlist_title
                    if AuthorMark:
                        out = f"{author_name} - {out}"
                    if PlatformMark:
                        out = f"{out} (Youtube Music: {playlist_id})"
                    return out
                except Exception:
                    log(url_to_name.log_tag, f"Повторная попытка создать имя через {ErrorSleep} секунд.")
                    time.sleep(ErrorSleep)
#Обложки
def download_soundcloud_cover(url):
    log_tag = "SC Cover"
    path = os.path.join(dirs_paths.SoundCloud_Covers, f"{url_to_name.soundcloud_track(url)}_cover.jpg")
    if os.path.exists(path):
        log(log_tag, f"Обложка уже существует: {path}")
        return path
    log(log_tag, "Получение информации.")
    info = None
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while info == None:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    log(log_tag, "Получение ссылки на изображение")
    img_url = info.get('thumbnail')
    log(log_tag, f"Ссылка на изображение: {img_url}")
    if img_url:
        while True:
            try:
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB')
                img.save(path, 'JPEG')
                log(log_tag, f"Обложка сохранена: {path}.")
                return path
            except Exception as e:
                log(log_tag, f"Не удалось обработать обложку: {e}.")
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    return None
def download_youtube_cover(url):
    log_tag = "Yt Cover"
    path = os.path.join(dirs_paths.Youtube_Covers, f"{url_to_name.youtube_track(url)}_cover.jpg")
    if os.path.exists(path):
        log(log_tag, f"Обложка уже существует: {path}")
        return path
    log(log_tag, "Получение информации.")
    info = None
    with yt_dlp.YoutubeDL(ydl_opts.youtube_cover) as ydl:
        while info == None:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    log(log_tag, "Получение id.")
    video_id = info.get('id')
    try:
        qualities = ['maxresdefault', 'sddefault', 'hqdefault', 'mqdefault', 'default']
        for quality in qualities:
            img_url = f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"
            log(log_tag, f"Скачивание {quality}")
            try:
                response = requests.get(img_url, timeout=5)
                while response.status_code == 403:
                    log(log_tag, f"Ошибка 403 через {ErrorSleep} секунд ещё одна попытка")
                    time.sleep(ErrorSleep)
                    response = requests.get(img_url, timeout=5)
                log(log_tag, f"Сервер ответил со статусом: {response.status_code}")
                if response.status_code == 200:
                    temp_img = Image.open(BytesIO(response.content))
                    if temp_img.size == (120, 90):
                        log(log_tag, f"Качество {quality} выдало заглушку. Пробуем ниже.")
                        continue
                    img = temp_img.convert('RGB')
                    img.save(path, 'JPEG')
                    log(log_tag, f"Найдено реальное качество ({quality}) с разрешением: {img.size}")
                    break
                else:
                    log(log_tag, f"Статус {response.status_code} для {quality}, пробуем хуже.")
                    continue
            except Exception:
                log(log_tag, "ухужшение качества.")
                continue
        log(log_tag, f"Исходная обложка сохранена: {path}")
        
        with Image.open(path) as saved_img: 
            '''
            Эту микро обрезку (если 4:3) я попросил сдлелать Gemini (только логи мои)
            и я не очень разбираюсь как она работает,
            а ещё она не работает на шортсах
            '''
            w, h = saved_img.width, saved_img.height
            current_ratio = w / h
            if abs(current_ratio - 1.333) < 0.05:
                log(log_tag, f"Похоже обложка 4:3 и есть шанс что она на самом деле имеет особое соотнощшение сторон")
                img_np = numpy.array(saved_img)
                row_stds = numpy.std(img_np, axis=(1, 2))
                row_means = numpy.mean(img_np, axis=(1, 2))
                is_black_row = (row_stds < 12) & (row_means < 15)
                top_black_lines = 0
                for row in is_black_row:
                    if row:
                        top_black_lines += 1
                    else:
                        break
                bottom_black_lines = 0
                for row in reversed(is_black_row):
                    if row:
                        bottom_black_lines += 1
                    else:
                        break
                col_stds = numpy.std(img_np, axis=(0, 2))
                col_means = numpy.mean(img_np, axis=(0, 2))
                is_black_col = (col_stds < 12) & (col_means < 15)
                
                left_black_lines = 0
                for col in is_black_col:
                    if col:
                        left_black_lines += 1
                    else:
                        break
                right_black_lines = 0
                for col in reversed(is_black_col):
                    if col:
                        right_black_lines += 1
                    else:
                        break
                if top_black_lines > 0 or bottom_black_lines > 0 or left_black_lines > 0 or right_black_lines > 0:
                    cropped_img = saved_img.crop((left_black_lines, top_black_lines, w - right_black_lines, h - bottom_black_lines))
                    cropped_img.save(path, 'JPEG')
        return path
    except Exception:
        pass
    return None
def download_youtubemusic_cover(url): # Скачивание ютуб обложки от видео вместе с вырезанем её под квадрат
    log_tag = "Yt Music Cover"
    path = os.path.join(dirs_paths.YoutubeMusic_Covers, f"{url_to_name.youtube_track(url)}_cover.jpg")
    if os.path.exists(path):
        log(log_tag, f"Обложка уже существует: {path}")
        return path

    log(log_tag, f"Скачивание Обложки с ютуб")
    img_file = download_youtube_cover(url)

    if img_file and os.path.exists(img_file):
        try:
            log(log_tag, f"Исходный файл найден ({img_file}). Начало анализа краев.")
            with Image.open(img_file) as img:
                img = img.convert("RGB")
                width, height = img.size
                log(log_tag, f"Размеры картинки: {width}x{height}")
                
                if width > height:
                    img_np = numpy.array(img)
                    crop_needed = width - height
                    left_margin = crop_needed // 2
                    right_margin = width - (crop_needed - left_margin)
                    
                    left_zone = img_np[:, :left_margin]
                    right_zone = img_np[:, right_margin:]
                    
                    is_left_empty = numpy.all(numpy.std(left_zone, axis=(0, 1)) < 15)
                    is_right_empty = numpy.all(numpy.std(right_zone, axis=(0, 1)) < 15)

                    log(log_tag, f"Анализ пустоты по бокам: Лево={is_left_empty}, Право={is_right_empty}")
                    
                    if is_left_empty and is_right_empty:
                        log(log_tag, f"По бокам пусто. Обрезаем картинку под квадрат.")
                        img_final = img.crop((left_margin, 0, right_margin, height))
                    else:
                        log(log_tag, f"Обнаружены детали по бокам. Достраиваем полями сверху/снизу.")
                        bg_color = img.resize((1, 1), resample=3).getpixel((0, 0))
                        img_final = Image.new("RGB", (width, width), bg_color)
                        img_final.paste(img, (0, (width - height) // 2))
                        
                elif width < height:
                    log(log_tag, f"Картинка вертикальная. Начало анализа верхних и нижних полей.")
                    img_np = numpy.array(img)
                    crop_needed = height - width
                    top_margin = crop_needed // 2
                    bottom_margin = height - (crop_needed - top_margin)
                    
                    top_zone = img_np[:top_margin, :]
                    bottom_zone = img_np[bottom_margin:, :]
                    
                    is_top_empty = numpy.all(numpy.std(top_zone, axis=(0, 1)) < 15)
                    is_bottom_empty = numpy.all(numpy.std(bottom_zone, axis=(0, 1)) < 15)
                    
                    log(log_tag, f"Анализ пустоты сверху/снизу: Верх={is_top_empty}, Низ={is_bottom_empty}")
                    
                    if is_top_empty and is_bottom_empty:
                        log(log_tag, f"Сверху и снизу пусто. Обрезаем картинку под квадрат.")
                        img_final = img.crop((0, top_margin, width, bottom_margin))
                    else:
                        log(log_tag, f"Обнаружены детали сверху/снизу. Достраиваем полями по бокам.")
                        bg_color = img.resize((1, 1), resample=3).getpixel((0, 0))
                        img_final = Image.new("RGB", (height, height), bg_color)
                        img_final.paste(img, ((height - width) // 2, 0))
                else:
                    log(log_tag, f"Картинка уже квадратная. Оставляем оригинал.")
                    img_final = img
                
                img_final.save(path, "JPEG", quality=95)
                log(log_tag, f"Финальный квадрат сохранен: {path}")
                return path
        except Exception:
            pass
    else:
        log(log_tag, f"Ошибка: Обложка не была скачана")
    return None
#mp3
def download_soundcloud_mp3(url):
    filename = url_to_name.soundcloud_track(url)
    log_tag = "SC mp3"
    path = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.mp3")
    if os.path.exists(path):
        log(log_tag, f"mp3 файл уже существует: {path}")
        return path
    opts = ydl_opts.soundcloud_audio_track.copy()
    opts['outtmpl'] = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.%(ext)s")
    log(log_tag, f"Скачивание mp3 с SoundCloud: {filename}.")
    with yt_dlp.YoutubeDL(opts) as ydl:
        while True:
            try:
                ydl.download([url])
                return path
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    return None
def download_youtube_mp3(url):
    log_tag = "Yt mp3"

    filename = url_to_name.youtube_track(url)
    path = os.path.join(dirs_paths.Youtube_Music, f"{filename}.mp3")
    
    if os.path.exists(path):
        log(log_tag, f"mp3 файл уже существует: {path}")
        return path
    opts = ydl_opts.youtube_audio_track.copy()
    opts['outtmpl'] = os.path.join(dirs_paths.Youtube_Music, f"{filename}.%(ext)s")
    with yt_dlp.YoutubeDL(opts) as ydl:
        while True:
            try:
                ydl.download([url])
                return path
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    return None
#mp3 с встроенной информацией
def download_soundcloud_track_with_info(url):
    log_tag = "SC track with info"
    info = None
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while info == None:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)

    path = download_soundcloud_mp3(url)
    img_file = download_soundcloud_cover(url)

    try:
        log(log_tag, "Удаление данных.")
        audio = mutagen.id3.ID3(path)
        audio.delete()
        log(log_tag, "Заполнение данных.")
        audio = mutagen.id3.ID3()
        audio.add(mutagen.id3.TPE1(encoding=3, text=info.get('uploader', 'Unknown Author')))  
        audio.add(mutagen.id3.TIT2(encoding=3, text=info.get('title', 'Track')))   
        audio.add(mutagen.id3.TALB(encoding=3, text="SoundCloud"))    
        if img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as f:
                audio.add(mutagen.id3.APIC(
                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                ))
        audio.save(path, v2_version=3)
        log(log_tag, "Обложка и теги успешно вшиты в MP3.")
    except Exception:
        log(log_tag, f"Не удалось записать теги.")

    return path
def download_youtube_track_with_info(url):
    log_tag = "Yt Music track with info"

    track_opts = ydl_opts.youtube_info.copy()
    track_opts['noplaylist'] = True
    path = download_youtube_mp3(url)

    with yt_dlp.YoutubeDL(track_opts) as ydl:
        attempt = 0
        while True:
            try:
                info = ydl.extract_info(url, download=False)
                break
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)

    img_file = download_youtubemusic_cover(url)   

    try:
        log(log_tag, "Удаление данных...")
        audio = mutagen.id3.ID3(path)
        audio.delete()
        log(log_tag, "Заполнение данных...")
        audio = mutagen.id3.ID3()
        audio.add(mutagen.id3.TPE1(encoding=3, text=info.get('uploader', 'Unknown Author')))  
        audio.add(mutagen.id3.TIT2(encoding=3, text=info.get('title', 'Untitled Video')))   
        audio.add(mutagen.id3.TALB(encoding=3, text="YouTube"))       
        
        if img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as f:
                audio.add(mutagen.id3.APIC(
                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                ))
        audio.save(path, v2_version=3)
        log(log_tag, "Обложка и теги успешно вшиты в MP3!")
    except Exception:
        log(log_tag, f"Не удалось записать теги.")
    return path
#Скачивание лейлистов
def download_soundcloud_playlist(url, params):
    log_tag = "SC playlist"
    playlist_info = None
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while not playlist_info:
            try:
                playlist_info = ydl.extract_info(url, download=False)
                break
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)

    playlist_unique_title = url_to_name.soundcloud_playlist_for_info(url,params["AddAuthorNameAtTheStart"],params["AddPlatformNameAndIdToAlbumName"])
    if params["SaveToFolder"]:
        target_dir = os.path.join(dirs_paths.SoundCloud_Music, url_to_name.soundcloud_playlist_folder(url))
        os.makedirs(target_dir, exist_ok=True)
    else:
        target_dir = dirs_paths.SoundCloud_Music

    entries = list(playlist_info['entries'])
    total_tracks = len(entries)
    padding_width = len(str(total_tracks))

    log(log_tag, f"\nНачало обработки плейлиста: {playlist_unique_title} (Всего треков: {total_tracks})")
    for index, entry in enumerate(entries, start=1):
        try:
            str_index = str(index).zfill(padding_width)
            if not entry:
                continue
            track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
            if not track_url:
                continue

            
            
            filename = url_to_name.soundcloud_track(track_url)
            mp3_file = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.mp3")

            download_soundcloud_track_with_info(track_url)

            current_name = os.path.basename(mp3_file)
            
            if params["AddIndexAttheStartOfFilesNames"]:
                new_name = f"{str_index} {current_name}"
            else:
                new_name = current_name
                
            target_file_path = os.path.join(target_dir, new_name)
            
            if params["SaveToFolder"] or params["AddIndexAttheStartOfFilesNames"]:
                if os.path.exists(target_file_path):
                    os.remove(target_file_path)
                shutil.copy(mp3_file, target_file_path)
                mp3_file = target_file_path

            if params["PlaylistnameIsAlbum"]:
                try:
                    try:
                        audio = mutagen.id3.ID3(mp3_file)
                    except mutagen.id3.ID3NoHeaderError:
                        audio = mutagen.id3.ID3()

                    orig_artist = str(audio.get('TPE1', entry.get('uploader', 'Unknown Author')))
                    orig_title = str(audio.get('TIT2', entry.get('title', 'Track')))
                    audio.add(mutagen.id3.TPE1(encoding=3, text=orig_artist))
                    if params["AddIndexAttheStartOfSongsNames"]:
                        audio.add(mutagen.id3.TIT2(encoding=3, text=f"{str_index} {orig_title}"))
                    else:
                        audio.add(mutagen.id3.TIT2(encoding=3, text=orig_title))
                    audio.add(mutagen.id3.TALB(encoding=3, text=playlist_unique_title))
                    audio.add(mutagen.id3.TRCK(encoding=3, text=str_index))
                    with open(download_soundcloud_cover(track_url), 'rb') as f:
                        audio.add(mutagen.id3.APIC(
                            encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                        ))
                    audio.save(mp3_file, v2_version=3)
                except Exception as e:
                    log(log_tag, f"Не удалось скорректировать альбомные теги: {e}")
        except Exception as trackerror:
            log(log_tag, f"{track_url}")
    return True
def download_youtube_music_playlist(url, params):
    log_tag = "Yt Music playlist"
    playlist_info = None
    log(log_tag, "Получение информации плейлиста")
    log(log_tag, "!!!Если в плейлисте есть хотя-бы одно скрытое видео скрипт сломается (у меня пока нет возможностиэто решить)!!!")
    with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
        while not playlist_info:
            try:
                playlist_info = ydl.extract_info(url, download=False)
                break
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    playlist_title = playlist_info.get('title', 'Untitled Playlist')
    playlist_unique_title = url_to_name.youtube_playlist_for_info(url,params["AddAuthorNameAtTheStart"],params["AddPlatformNameAndIdToAlbumName"])
    safe_name = url_to_name.youtube_playlist(url)
    
    if params["SaveToFolder"]:
        target_dir = os.path.join(dirs_paths.Youtube_Music, safe_name)
        os.makedirs(target_dir, exist_ok=True)
    else:
        target_dir = dirs_paths.Youtube_Music

    entries = list(playlist_info['entries'])
    total_tracks = len(entries)
    padding_width = len(str(total_tracks))
    playlist_title = playlist_info.get('title', 'Untitled Playlist')

    log(log_tag, f"Начало обработки плейлиста YouTube: {playlist_title} (Всего треков: {total_tracks})")
    
    for index, entry in enumerate(entries, start=1):
        if not entry:
            continue
            
        video_id = entry.get('id') or entry.get('video_id')
        if not video_id:
            continue
            
        track_url = f"https://www.youtube.com/watch?v={video_id}"
        str_index = str(index).zfill(padding_width)
        
        try:
            filename = url_to_name.youtube_track(track_url)
            filename = makesafename(filename)
            mp3_file = os.path.join(dirs_paths.Youtube_Music, f"{filename}.mp3")

            if os.path.exists(mp3_file):
                time.sleep(10)
            else:
                Exists = download_youtube_track_with_info(track_url)
                log(log_tag,Exists)
                while Exists == None:
                    log(log_tag, "Повторная попытка через 30 секунд")
                    time.sleep(30)
                    Exists = download_youtube_track_with_info(track_url)
                time.sleep(10)

            if mp3_file and os.path.exists(mp3_file):
                if not os.path.exists(os.path.join(dirs_paths.YoutubeMusic_Covers, f"{filename}_cover.jpg")):
                    img_file = download_youtubemusic_cover(track_url)
                else:
                    img_file = os.path.join(dirs_paths.YoutubeMusic_Covers, f"{filename}_cover.jpg")

                if params["PlaylistnameIsAlbum"]:
                    try:
                        audio = mutagen.id3.ID3(mp3_file)
                        audio.delete()
                        audio = mutagen.id3.ID3()
                        orig_artist = str(audio.get('TPE1', entry.get('uploader', 'Unknown Author')))
                        orig_title = str(audio.get('TIT2', entry.get('title', 'Track')))
                        audio.add(mutagen.id3.TPE1(encoding=3, text=orig_artist))
                        if params["AddIndexAttheStartOfSongsNames"]:
                            audio.add(mutagen.id3.TIT2(encoding=3, text=f"{str_index} {orig_title}"))
                        else:
                            audio.add(mutagen.id3.TIT2(encoding=3, text=orig_title))
                        audio.add(mutagen.id3.TALB(encoding=3, text=playlist_unique_title))
                        audio.add(mutagen.id3.TRCK(encoding=3, text=str_index))
                        
                        if img_file and os.path.exists(img_file):
                            with open(img_file, 'rb') as f:
                                audio.add(mutagen.id3.APIC(
                                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                                ))
                        audio.save(mp3_file, v2_version=3)
                    except Exception as e:
                        log(log_tag, f"Не удалось скорректировать альбомные теги: {e}")

                import shutil
                current_name = os.path.basename(mp3_file)
                
                if params["AddIndexAttheStartOfFilesNames"]:
                    new_name = f"{str_index} {current_name}"
                else:
                    new_name = current_name
                    
                target_file_path = os.path.join(target_dir, new_name)
                
                if params["SaveToFolder"] or params["AddIndexAttheStartOfFilesNames"]:
                    if os.path.exists(target_file_path):
                        os.remove(target_file_path)
                    shutil.copy(mp3_file, target_file_path)

        except:
            pass
            
    log(log_tag, f"\nСкачивание плейлиста завершено!")
    return True
#m3u
def create_soundcloud_m3u_playlist(url, music_dir=""):
    log_tag = "SC m3u"
    playlist_info = None
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        while not playlist_info:
            try:
                playlist_info = ydl.extract_info(url, download=False)
                break
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    with open(files_paths.SoundCloud_Music_dir_conf, 'r+', encoding='utf-8') as f:
        if music_dir == "":
            music_dir = f.read().strip()
        else:
            f.write(music_dir)
    m3u_file_path = os.path.join(dirs_paths.SoundCloud_Playlists, f"{url_to_name.soundcloud_playlist_folder(url)}.m3u")
    m3u_content = f"#EXTM3U\n#PLAYLIST:{url_to_name.soundcloud_playlist_for_info(url)}\n"
    log(log_tag, f"Начало создание контента файла {m3u_file_path}")
    for entry in playlist_info['entries']:
        if not entry:
            continue
        track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
        if not track_url:
            log(log_tag, "Ссылка на трек почему-то не была получена.")
            continue
        filename = url_to_name.soundcloud_track(track_url)
        log(log_tag, f"Файл {filename}.mp3.")
        full_path = os.path.normpath(os.path.join(music_dir, f"{filename}.mp3"))
        m3u_content += f"{full_path}\n"
    try:
        with open(m3u_file_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        return m3u_file_path
    except Exception:
        return None
def create_youtube_m3u_playlist(url, music_dir=""):
    log_tag = "Yt Music m3u"
    playlist_info = None
    log(log_tag, "Получение информации плейлиста")
    log(log_tag, "!!!Если в плейлисте есть хотя-бы одно скрытое видео скрипт сломается (у меня пока нет возможностиэто решить)!!!")
    with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
        while not playlist_info:
            try:
                playlist_info = ydl.extract_info(url, download=False)
                break
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
    with open(files_paths.Youtube_Music_dir_conf, 'r+', encoding='utf-8') as f:
        if music_dir == "":
            if os.path.exists(files_paths.Youtube_Music_dir_conf) and os.path.getsize(files_paths.Youtube_Music_dir_conf) > 0:
                music_dir = f.read().strip()
            if not music_dir or music_dir.startswith("Путь к"):
                music_dir = dirs_paths.Youtube_Music
        else:
            f.write(music_dir)
    m3u_file_path = os.path.join(dirs_paths.Youtube_Playlists, f"{url_to_name.youtube_playlist_folder(url)}.m3u")
    m3u_content = f"#EXTM3U\n#PLAYLIST:{url_to_name.youtube_playlist_for_info(url)}\n"

    for entry in playlist_info['entries']:
        if not entry:
            continue
        track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
        if not track_url:
            log(log_tag, "Ссылка на трек почему-то не была получена.")
            continue

        filename = url_to_name.youtube_track(track_url)
        log(log_tag, f"Файл {filename}.mp3.")
        full_path = os.path.normpath(os.path.join(music_dir, f"{filename}.mp3"))
        m3u_content += f"{full_path}\n"
    try:
        with open(m3u_file_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        return m3u_file_path
    except Exception:
        return None

#Скачивание видео
def download_rutube_video(url):
    log_tag = "Rutube Video"
    filename = url_to_name.rutube_video(url)
    path = os.path.join(dirs_paths.Rutube_Videos, f"{filename}.%(ext)s")
    existing_files = glob.glob(os.path.join(dirs_paths.Rutube_Videos, f"{filename}.*"))
    if existing_files:
        log(log_tag, f"Видео уже существует: {existing_files[0]}")
        return existing_files[0]
    opts = ydl_opts.rutube_video_track
    opts['outtmpl'] = path
    log(log_tag, f"Начало скачивания.")
    with yt_dlp.YoutubeDL(opts) as ydl:
        while True:
            try:
                ydl.download([url])
                log(log_tag, f"Видео успешно скачалось.")
                return path
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
def download_vk_video(url):
    log_tag = "VK Video"
    filename = url_to_name.vk_video(url)
    path = os.path.join(dirs_paths.VK_Videos, f"{filename}.%(ext)s")
    existing_files = glob.glob(os.path.join(dirs_paths.VK_Videos, f"{filename}.*"))
    if existing_files:
        log(log_tag, f"Видео уже существует: {existing_files[0]}")
        return existing_files[0]
    opts = ydl_opts.vk_video_track
    opts['outtmpl'] = path
    log(log_tag, f"Начало скачивания.")
    with yt_dlp.YoutubeDL(opts) as ydl:
        while True:
            try:
                ydl.download([url])
                log(log_tag, f"Видео успешно скачалось.")
                return path
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
def download_youtube_video(url):
    log_tag = "Yt Video"
    filename = url_to_name.youtube_video(url)
    path = os.path.join(dirs_paths.Youtube_Videos, f"{filename}.%(ext)s")
    existing_files = glob.glob(os.path.join(dirs_paths.Youtube_Videos, f"{filename}.*"))
    if existing_files:
        log(log_tag, f"Видео уже существует: {existing_files[0]}")
        return existing_files[0]
    opts = ydl_opts.youtube_video_track
    opts['outtmpl'] = path
    log(log_tag, f"Начало скачивания.")
    with yt_dlp.YoutubeDL(opts) as ydl:
        while True:
            try:
                ydl.download([url])
                log(log_tag, f"Видео успешно скачалось.")
                return path
            except Exception:
                log(log_tag, f"Повторная попытка через {ErrorSleep} секунд.")
                time.sleep(ErrorSleep)
#Плейлисты с видео
def download_youtube_video_playlist(url):
    log_tag = "Yt Video Playlist"
    opts = ydl_opts.youtube_video_track.copy()
    opts['noplaylist'] = False
    opts['outtmpl'] = os.path.join(dirs_paths.Youtube_Videos, "%(title)s [%(id)s].%(ext)s")
    print(f"Скачивание видео-плейлиста: {url_to_name.youtube_playlist_for_info(url)}...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])