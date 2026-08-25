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

#Доп функции
def log(tag,text,spacecount = 16):
    if len(tag) > spacecount:
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
        log("links from file",f"Ошибка: Файл не найден: {file_path}")
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
#Парамептры для модуля - yt_dlp
class ydl_opts():
    _base = {
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': dirs_paths.bin,
    }
    soundcloud_info = {
        **_base,
        'extract_flat': 'in_playlist',
        'skip_download': True,
    }
    youtube_info = {
        **_base,
        'skip_download': True,
    }   
    youtube_cover = {
        **_base,
        'noplaylist': True,
        'extract_flat': False,
    }

    soundcloud_audio_track = {
        **_base,
        'noplaylist': True,
        'format': 'http_mp3_128/hls_mp3_128/hls_opus_64/bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '192',
        }],
    }
    soundcloud_audio_playlist = {
        **_base,
        'noplaylist': False,
        'format': 'http_mp3_128/hls_mp3_128/hls_opus_64/bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '192',
        }],
    }
    youtube_audio_track = {
        **_base,
        'noplaylist': True,
        'format': 'bestaudio/ba/worstaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '192',
        }],
    }
    youtube_video_track = {
        **_base,
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
    @staticmethod
    def youtube_video(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Untitled Video')
            v_id = info.get('id', 'unknown_id')
            return f"{makesafename(video_title)} [{v_id}]"
        except Exception:
            return "youtube_video"
    @staticmethod
    def youtube_track(url):
        try:
            track_opts = ydl_opts.youtube_info.copy()
            track_opts['noplaylist'] = True
            
            with yt_dlp.YoutubeDL(track_opts) as ydl:
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
            return "youtube_track"
    @staticmethod
    def youtube_playlist(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            playlist_title = info.get('title', 'Untitled Playlist')
            playlist_id = info.get('id', 'unknown_id')
            return makesafename(f"{playlist_title} {playlist_id}")
        except Exception:
            return "youtube_playlist"

    @staticmethod
    def rutube_video(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.rutube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            video_id = info.get('id', 'unknown_id')
            video_title = info.get('title', 'Untitled Video')
            return f"{makesafename(video_title)} [{video_id}]"
        except Exception:
            return "rutube_video"

    @staticmethod
    def vk_video(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.vk_info) as ydl:
                info = ydl.extract_info(url, download=False)
            video_id = info.get('id', 'unknown_id')
            video_title = info.get('title', 'Untitled Video')
            return f"{makesafename(video_title)} [{video_id}]"
        except Exception:
            return "vk_video"

    @staticmethod
    def soundcloud_track(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
                info = ydl.extract_info(url, download=False)
            normal_url = info.get('webpage_url', url)
            path_parts = [p for p in urlparse(normal_url).path.split('/') if p]
            artist_slug = path_parts[-2] if len(path_parts) >= 2 else "artist"
            track_slug = path_parts[-1].split('?')[0] if path_parts else "track"
            return makesafename(f"{artist_slug} {track_slug}")
        except Exception:
            return "soundcloud_track"

    @staticmethod
    def soundcloud_playlist(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
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
            return "soundcloud_playlist"
    @staticmethod
    def soundcloud_playlist_for_info(url,AuthorMark=False,PlatformMark=False):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
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
            return "soundcloud_playlist"

    @staticmethod
    def youtube_playlist_for_info(url,AuthorMark=False,PlatformMark=False):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
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
            return "youtube_playlist"
#Обложки
def download_soundcloud_cover(url):
    log_tag = "SC Cover"
    path = os.path.join(dirs_paths.SoundCloud_Covers, f"{url_to_name.soundcloud_track(url)}_cover.jpg")
    if os.path.exists(path):
        log(log_tag,f"Обложка уже существует: {path}")
        return path
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        info = ydl.extract_info(url, download=False)
    img_url = info.get('thumbnail')
    if img_url:
        try:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            img.save(path, 'JPEG')
            log(log_tag,f"Обложка сохранена: {path}")
            return path
        except Exception as e:
            log(log_tag,f"Не удалось обработать обложку: {e}")
    return None
def download_youtube_cover(url):
    log_tag = "Yt Cover"
    path = os.path.join(dirs_paths.Youtube_Covers, f"{url_to_name.youtube_track(url)}_cover.jpg")
    if os.path.exists(path):
        log(log_tag, f"Обложка уже существует: {path}")
        return path

    log(log_tag, f"Получение id через yt-dlp для: {url}")
    with yt_dlp.YoutubeDL(ydl_opts.youtube_cover) as ydl:
        info = ydl.extract_info(url, download=False)
    video_id = info.get('id')

    try:
        qualities = ['maxresdefault', 'sddefault', 'hqdefault', 'mqdefault', 'default']
        for quality in qualities:
            img_url = f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"
            log(log_tag, f"Скачивание {quality}")
            try:
                response = requests.get(img_url, timeout=5)
                while response.status_code == 403:
                    log(log_tag, f"Ошибка 403 через 30 секунд ещё одна попытка")
                    time.sleep(30)
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
            except requests.RequestException:
                log(log_tag,"Какая-то ошибка, ухужшение качества.")
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
    except Exception as e:
        log(log_tag, f"Ошибка при скачивании/сохранении файла: {e}")
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
            log(log_tag, f"Исходный файл найден ({img_file}). Начало анализа краев...")
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
                        log(log_tag, f"По бокам пусто. Обрезаем картинку под квадрат...")
                        img_final = img.crop((left_margin, 0, right_margin, height))
                    else:
                        log(log_tag, f"Обнаружены детали по бокам. Достраиваем полями сверху/снизу...")
                        bg_color = img.resize((1, 1), resample=3).getpixel((0, 0))
                        img_final = Image.new("RGB", (width, width), bg_color)
                        img_final.paste(img, (0, (width - height) // 2))
                        
                elif width < height:
                    log(log_tag, f"Картинка вертикальная. Начало анализа верхних и нижних полей...")
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
                        log(log_tag, f"Сверху и снизу пусто. Обрезаем картинку под квадрат...")
                        img_final = img.crop((0, top_margin, width, bottom_margin))
                    else:
                        log(log_tag, f"Обнаружены детали сверху/снизу. Достраиваем полями по бокам...")
                        bg_color = img.resize((1, 1), resample=3).getpixel((0, 0))
                        img_final = Image.new("RGB", (height, height), bg_color)
                        img_final.paste(img, ((height - width) // 2, 0))
                else:
                    log(log_tag, f"Картинка уже квадратная. Оставляем оригинал.")
                    img_final = img
                
                img_final.save(path, "JPEG", quality=95)
                log(log_tag, f"Финальный квадрат сохранен: {path}")
                return path
        except Exception as e:
            log(log_tag, f"Ошибка в процессе обработки квадрата: {e}")
    else:
        log(log_tag, f"Ошибка: Обложка не была скачана")
    return None
#mp3
def download_soundcloud_mp3(url):
    log_tag = "SC mp3"
    info = None
    while info == None:
        try:
            with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
                info = ydl.extract_info(url, download=False)
            break
        except Exception as e:
            log(log_tag, f"Ошибка, через 30 секунд ещё одна попытка")
            time.sleep(30)
    ext = info.get('ext')
    filename = url_to_name.soundcloud_track(url)
    path = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.{ext}")
    if os.path.exists(path):
        log(log_tag,f"файл уже существует, пропускаем: {path}")
        return path
    os.makedirs(dirs_paths.SoundCloud_Music, exist_ok=True)
    save_path = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.%(ext)s")
    opts = ydl_opts.soundcloud_audio_track.copy()
    opts['outtmpl'] = save_path
    log(log_tag,f"Скачивание mp3 с SoundCloud: {filename}...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
        return path
    return None
def download_youtube_mp3(url):
    log_tag = "Yt mp3"
    filename = url_to_filename.youtube_track(url)
    path = os.path.join(dirs_paths.Youtube_Music, f"{filename}.mp3")

    if os.path.exists(path):
        log(log_tag,f"Трек YouTube уже существует, пропускаем: {path}")
        return path

    os.makedirs(dirs_paths.Youtube_Music, exist_ok=True)
    save_path = os.path.join(dirs_paths.Youtube_Music, f"{filename}.%(ext)s")
    
    opts = ydl_opts.youtube_audio_track.copy()
    opts['outtmpl'] = save_path
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
        return path
    return None
download_soundcloud_mp3("https://soundcloud.com/nekofard-archive/flower-man")