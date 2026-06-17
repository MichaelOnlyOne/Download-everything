import subprocess
import os
import sys
import time
from io import BytesIO
from urllib.parse import urlparse, parse_qs

def check_and_download_modules(modules = ["requests",'yt-dlp', 'mutagen', 'PIL', 'regex', 'moviepy']):
    for module in modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            pip_name = 'pillow' if module == 'PIL' else module
            print(f"Sorry didn't you download {pip_name}, but downloading strarts")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "--quiet"])
check_and_download_modules()
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
import yt_dlp
import requests
import re
import regex
import mutagen


class dirs_paths():
    __base_dir__ = os.path.dirname(os.path.abspath(__file__))
    bin = os.path.join(__base_dir__,'.bin')
    Playlists = os.path.join(__base_dir__,"Playlists")
    Videos = os.path.join(__base_dir__,"Videos")
    Music = os.path.join(__base_dir__,"Music")
    Covers = os.path.join(__base_dir__,"Covers")
    confs = os.path.join(__base_dir__,".conf")
    inputs = os.path.join(__base_dir__,"Input Files")
    Youtube_Covers = os.path.join(__base_dir__,"Covers","Youtube")
    YoutubeMusic_Covers = os.path.join(__base_dir__,"Covers","YoutubeMusic")
    SoundCloud_Covers = os.path.join(__base_dir__,"Covers","SoundCloud")
    Rutube_Videos = os.path.join(__base_dir__,"Videos","Rutube")
    Youtube_Videos = os.path.join(__base_dir__,"Videos","Youtube")
    VK_Videos = os.path.join(__base_dir__,"Videos","VK")
    Youtube_Music = os.path.join(__base_dir__,"Music","Youtube")
    SoundCloud_Music = os.path.join(__base_dir__,"Music","SoundCloud")
    SoundCloud_Playlists = os.path.join(__base_dir__,"Playlists","SoundCloud")
    Youtube_Playlists = os.path.join(__base_dir__,"Playlists","Youtube")
class files_paths():
    SoundCloud_Music_dir_conf = os.path.join(dirs_paths.confs,"SoundCloud"+" Music Storage.txt")
    Youtube_Music_dir_conf = os.path.join(dirs_paths.confs,"Youtube"+" Music Storage.txt")
    SoundCloud_Playlists_links = os.path.join(dirs_paths.inputs,"SoundCloud"+" Playlists links.txt")
    Youtube_Music_Playlists_links = os.path.join(dirs_paths.inputs,"Youtube Music"+" Playlists links.txt")
    Youtube_Videos_links = os.path.join(dirs_paths.inputs,"Youtube"+" Videos links.txt")
    Rutube_Videos_links = os.path.join(dirs_paths.inputs,"Rutube"+" Videos links.txt")
    log = os.path.join(dirs_paths.__base_dir__,"log.txt")
def write_if_empty(file_path, text):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
def check_and_create_dirs_and_files():
    for attr in dir(dirs_paths):
        if not attr.startswith('__'):
            folder_path = getattr(dirs_paths, attr)
            if isinstance(folder_path, str):
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
    write_if_empty(files_paths.SoundCloud_Music_dir_conf, "Music/SoundCloud")
    write_if_empty(files_paths.Youtube_Music_dir_conf, "Music/Youtube")
    
    write_if_empty(files_paths.SoundCloud_Playlists_links, "# Вставьте сюда ссылки на плейлисты SoundCloud\n")
    write_if_empty(files_paths.Youtube_Music_Playlists_links, "# Вставьте сюда ссылки на плейлисты Youtube Music\n")
    write_if_empty(files_paths.Youtube_Videos_links, "# Вставьте сюда ссылки на видео Youtube\n")
    write_if_empty(files_paths.Rutube_Videos_links, "# Вставьте сюда ссылки на видео Rutube\n")
    write_if_empty(files_paths.log, "log\n")

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

check_and_create_dirs_and_files()

def read_links_from_file(file_path):
    links = []
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл не найден: {file_path}")
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
def inputnumber(count):
    while True:
        inp = input("> ")
        if not inp.isdigit():
            print("Введи число")
            continue
        val = int(inp)
        # range(1, count+1) проверяет строго от 1 до count
        if val not in range(1, count+1): 
            print(f"Введи число в диапазоне 1-{count}")
            continue
        return val # Возвращаем то, что ввел юзер, а не count!
def makesafename(safe_name):
    safe_name = safe_name.replace('/', '-').replace('\\', '-').replace(':', ' -')
    safe_name = regex.sub(r'[^\p{L}\p{N}\s\-\_ \(\)\[\]]', '', safe_name)
    safe_name = regex.sub(r'\s+', ' ', safe_name).strip()
    if len(safe_name) > 100:
        safe_name = safe_name[:100].strip()
        
    return safe_name


class url_to_filename:
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
        log_file = None
        try:
            log_file = open(files_paths.log, "a", encoding="utf-8")
            log_file.write(f"[START] Получен URL: {url}\n")
            log_file.flush()
            
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
            log_file.write(f"[SUCCESS] Сгенерировано имя: {result}\n")
            return result
        except Exception as e:
            if log_file:
                log_file.write(f"[ERROR] Сбой в методе youtube_track для URL {url}: {str(e)}\n")
            return "youtube_track"
        finally:
            if log_file:
                log_file.close()

    @staticmethod
    def youtube_playlist(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            playlist_title = info.get('title', 'Untitled Playlist')
            playlist_id = info.get('id', 'unknown_id')
            return makesafename(f"{playlist_title} [{playlist_id}]")
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
    def soundcloud_playlist_for_info(url):
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
            return f"{makesafename(playlist_title)} {playlist_id} "
        except Exception:
            return "soundcloud_playlist"

    @staticmethod
    def youtube_playlist_for_info(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            playlist_title = info.get('title', 'Untitled Playlist')
            playlist_id = info.get('id', 'unknown_id')
            return f"{makesafename(playlist_title)} {playlist_id} "
        except Exception:
            return "youtube_playlist"
def download_soundcloud_cover(url):
    filename = url_to_filename.soundcloud_track(url)
    filename = makesafename(filename)

    full_path = os.path.join(dirs_paths.SoundCloud_Covers, f"{filename}_cover.jpg")

    if os.path.exists(full_path):
        print(f"Обложка SoundCloud уже существует, пропускаем: {full_path}")
        return full_path

    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        info = ydl.extract_info(url, download=False)
    img_url = info.get('thumbnail')
    
    if img_url:
        os.makedirs(dirs_paths.SoundCloud_Covers, exist_ok=True)
        try:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            img.save(full_path, 'JPEG')
            print(f"Обложка SoundCloud сохранена: {full_path}")
            return full_path
        except Exception as e:
            print(f"Не удалось обработать обложку SoundCloud: {e}")
    return None
def download_youtube_cover(url):
    filename = url_to_filename.youtube_track(url)
    filename = makesafename(filename)

    full_path = os.path.join(dirs_paths.Youtube_Covers, f"{filename}_cover.jpg")

    if os.path.exists(full_path):
        print(f"[YouTube Cover] Файл обложки уже на диске: {full_path}")
        return full_path

    print(f"[YouTube Cover] Запрос метаданных через yt-dlp для: {url}...")
    with yt_dlp.YoutubeDL(ydl_opts.youtube_cover) as ydl:
        info = ydl.extract_info(url, download=False)
    
    img_url = info.get('thumbnail')
    print(f"[YouTube Cover] Получена ссылка на превью: {img_url}")
    
    if img_url:
        os.makedirs(dirs_paths.Youtube_Covers, exist_ok=True)
        try:
            print(f"[YouTube Cover] Скачивание картинки через requests...")
            response = requests.get(img_url, timeout=5)
            print(f"[YouTube Cover] Сервер ответил со статусом: {response.status_code}")
            
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            img.save(full_path, 'JPEG')
            print(f"[YouTube Cover] Базовая обложка успешно сохранена: {full_path}")
            return full_path
        except Exception as e:
            print(f"[YouTube Cover] Ошибка при скачивании/сохранении файла: {e}")
    else:
        print("[YouTube Cover] Предупреждение: В метаданных 'info' отсутствует поле 'thumbnail'!")
    return None


def download_youtubemusic_cover(url):
    filename = url_to_filename.youtube_track(url)
    filename = makesafename(filename)

    full_path = os.path.join(dirs_paths.YoutubeMusic_Covers, f"{filename}_cover.jpg")

    if os.path.exists(full_path):
        print(f"[YT Music Cover] Обложка уже на диске: {full_path}")
        return full_path

    os.makedirs(dirs_paths.YoutubeMusic_Covers, exist_ok=True)
    
    print("[YT Music Cover] Запуск базовой скачивалки download_youtube_cover...")
    img_file = download_youtube_cover(url)
    
    if img_file and os.path.exists(img_file):
        try:
            import numpy as np
            print(f"[YT Music Cover] Исходный файл найден ({img_file}). Начало анализа краев...")
            with Image.open(img_file) as img:
                img = img.convert("RGB")
                width, height = img.size
                print(f"[YT Music Cover] Размеры картинки: {width}x{height}")
                
                if width > height:
                    img_np = np.array(img)
                    crop_needed = width - height
                    left_margin = crop_needed // 2
                    right_margin = width - (crop_needed - left_margin)
                    
                    left_zone = img_np[:, :left_margin]
                    right_zone = img_np[:, right_margin:]
                    
                    is_left_empty = np.std(left_zone) < 15
                    is_right_empty = np.std(right_zone) < 15
                    print(f"[YT Music Cover] Анализ пустоты по бокам: Лево={is_left_empty}, Право={is_right_empty}")
                    
                    if is_left_empty and is_right_empty:
                        print("[YT Music Cover] По бокам пусто. Обрезаем картинку под квадрат...")
                        img_final = img.crop((left_margin, 0, right_margin, height))
                    else:
                        print("[YT Music Cover] Обнаружены детали по бокам. Достраиваем полями сверху/снизу...")
                        bg_color = img.getpixel((0, 0)) 
                        img_final = Image.new("RGB", (width, width), bg_color)
                        img_final.paste(img, (0, (width - height) // 2))
                else:
                    print("[YT Music Cover] Картинка уже квадратная или вертикальная. Оставляем оригинал.")
                    img_final = img
                
                img_final.save(full_path, "JPEG", quality=95)
                print(f"[YT Music Cover] Финальный квадрат сохранен: {full_path}")
                return full_path
        except Exception as e:
            print(f"[YT Music Cover] Ошибка в процессе обработки квадрата: {e}")
    else:
        print(f"[YT Music Cover] Ошибка: Базовая скачивалка вернула пустой путь или файл физически отсутствует!")
            
    return None

def download_rutube_video(url):
    filename = url_to_filename.rutube_video(url)
    filename = makesafename(filename)
    
    save_path = os.path.join(dirs_paths.Rutube_Videos, f"{filename}.%(ext)s")
    
    import glob
    existing_files = glob.glob(os.path.join(dirs_paths.Rutube_Videos, f"{filename}.*"))
    if existing_files:
        print(f"Видео Rutube уже существует, пропускаем: {existing_files[0]}")
        return existing_files[0]
        
    os.makedirs(dirs_paths.Rutube_Videos, exist_ok=True)
    opts = ydl_opts.rutube_video_track
    opts['outtmpl'] = save_path
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def download_vk_video(url):
    filename = url_to_filename.vk_video(url)
    filename = makesafename(filename)
    
    save_path = os.path.join(dirs_paths.VK_Videos, f"{filename}.%(ext)s")
    
    import glob
    existing_files = glob.glob(os.path.join(dirs_paths.VK_Videos, f"{filename}.*"))
    if existing_files:
        print(f"Видео VK уже существует, пропускаем: {existing_files[0]}")
        return existing_files[0]
        
    os.makedirs(dirs_paths.VK_Videos, exist_ok=True)
    opts = ydl_opts.vk_video_track
    opts['outtmpl'] = save_path
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def download_youtube_video(url):
    filename = url_to_filename.youtube_video(url)
    filename = makesafename(filename)

    save_path = os.path.join(dirs_paths.Youtube_Videos, f"{filename}.%(ext)s")
    
    import glob
    existing_files = glob.glob(os.path.join(dirs_paths.Youtube_Videos, f"{filename}.*"))
    if existing_files:
        print(f"Видео YouTube уже существует, пропускаем: {existing_files[0]}")
        return existing_files[0]

    os.makedirs(dirs_paths.Youtube_Videos, exist_ok=True)
    opts = ydl_opts.youtube_video_track
    opts['outtmpl'] = save_path
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def download_soundcloud_mp3(url):
    filename = url_to_filename.soundcloud_track(url)
    filename = makesafename(filename)

    final_mp3_path = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.mp3")

    if os.path.exists(final_mp3_path):
        print(f"Трек SoundCloud уже существует, пропускаем: {final_mp3_path}")
        return final_mp3_path

    os.makedirs(dirs_paths.SoundCloud_Music, exist_ok=True)
    save_path = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.%(ext)s")
    
    opts = ydl_opts.soundcloud_audio_track
    opts['outtmpl'] = save_path
    
    print(f"Скачивание MP3 с SoundCloud: {filename}...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
        return final_mp3_path
    return None
def download_youtube_mp3(url):
    filename = url_to_filename.youtube_track(url)
    filename = makesafename(filename)

    final_mp3_path = os.path.join(dirs_paths.Youtube_Music, f"{filename}.mp3")

    if os.path.exists(final_mp3_path):
        print(f"Трек YouTube уже существует, пропускаем: {final_mp3_path}")
        return final_mp3_path

    os.makedirs(dirs_paths.Youtube_Music, exist_ok=True)
    save_path = os.path.join(dirs_paths.Youtube_Music, f"{filename}.%(ext)s")
    
    opts = ydl_opts.youtube_audio_track.copy()
    opts['outtmpl'] = save_path
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
        return final_mp3_path
    return None

def download_soundcloud_track_with_info(url):
    filename = url_to_filename.soundcloud_track(url)
    filename = makesafename(filename)

    mp3_file = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.mp3")

    if os.path.exists(mp3_file):
        print(f"Трек SoundCloud уже существует, пропускаем метаданные: {mp3_file}")
        return mp3_file

    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        info = ydl.extract_info(url, download=False)

    download_soundcloud_mp3(url)

    if not os.path.exists(mp3_file):
        print(f"Ошибка: MP3 файл {mp3_file} SoundCloud не был создан.")
        return None

    img_file = download_soundcloud_cover(url)
    
    print("Заполнение метаданных SoundCloud...")
    try:
        try:
            audio = mutagen.id3.ID3(mp3_file)
            audio.delete() 
        except Exception:
            pass
        
        audio = mutagen.id3.ID3()
        audio.add(mutagen.id3.TPE1(encoding=3, text=info.get('uploader', 'Unknown Author')))  
        audio.add(mutagen.id3.TIT2(encoding=3, text=info.get('title', 'Track')))   
        audio.add(mutagen.id3.TALB(encoding=3, text="SoundCloud"))    
        
        if img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as f:
                audio.add(mutagen.id3.APIC(
                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                ))
        audio.save(mp3_file, v2_version=3)
        print("Обложка и теги успешно вшиты в MP3!")
    except Exception as e:
        print(f"Не удалось записать теги: {e}")

    return mp3_file
def download_youtube_track_with_info(url):
    filename = url_to_filename.youtube_track(url)
    filename = makesafename(filename)
    mp3_file = os.path.join(dirs_paths.Youtube_Music, f"{filename}.mp3")

    if os.path.exists(mp3_file):
        print(f"Трек YouTube уже существует, пропускаем всю обработку: {mp3_file}")
        return mp3_file

    track_opts = ydl_opts.youtube_info.copy()
    track_opts['noplaylist'] = True
    
    with yt_dlp.YoutubeDL(track_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
    mp3_file = download_youtube_mp3(url)
    
    if mp3_file is None or not os.path.exists(mp3_file):
        print("Ошибка: MP3 файл YouTube не был создан.")
        return None

    img_file = download_youtubemusic_cover(url)
    
    print("Заполнение метаданных YouTube...")
    try:
        try:
            audio = mutagen.id3.ID3(mp3_file)
            audio.delete() 
        except Exception:
            pass
        
        audio = mutagen.id3.ID3()
        audio.add(mutagen.id3.TPE1(encoding=3, text=info.get('uploader', 'Unknown Author')))  
        audio.add(mutagen.id3.TIT2(encoding=3, text=info.get('title', 'Untitled Video')))   
        audio.add(mutagen.id3.TALB(encoding=3, text="YouTube"))       
        
        if img_file and os.path.exists(img_file):
            with open(img_file, 'rb') as f:
                audio.add(mutagen.id3.APIC(
                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                ))
        audio.save(mp3_file, v2_version=3)
        print("Обложка и теги успешно вшиты в MP3!")
    except Exception as e:
        print(f"Не удалось записать теги: {e}")

    return mp3_file

def download_soundcloud_playlist(url, save_to_folder=True, use_album_meta=True, add_index_to_filename=True):
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        
    if not playlist_info or 'entries' not in playlist_info:
        print("Ошибка: Не удалось загрузить информацию о плейлисте.")
        return None

    safe_name = url_to_filename.soundcloud_playlist(url)
    playlist_unique_title = url_to_filename.soundcloud_playlist_for_info(url)
    if save_to_folder:
        target_dir = os.path.join(dirs_paths.SoundCloud_Music, safe_name)
        os.makedirs(target_dir, exist_ok=True)
    else:
        target_dir = dirs_paths.SoundCloud_Music

    entries = list(playlist_info['entries'])
    total_tracks = len(entries)
    padding_width = len(str(total_tracks))
    playlist_title = playlist_info.get('title', 'Untitled Playlist')

    print(f"\nНачало обработки плейлиста: {playlist_title} (Всего треков: {total_tracks})")
    for index, entry in enumerate(entries, start=1):
        try:
            if not entry:
                continue
                
            track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
            if not track_url:
                continue
                
            str_index = str(index).zfill(padding_width)
            
            filename = url_to_filename.soundcloud_track(track_url)
            filename = makesafename(filename)
            mp3_file = os.path.join(dirs_paths.SoundCloud_Music, f"{filename}.mp3")

            if os.path.exists(mp3_file):
                time.sleep(3)
            else:
                time.sleep(10)
                download_soundcloud_track_with_info(track_url)

            if mp3_file and os.path.exists(mp3_file):
                if not os.path.exists(os.path.join(dirs_paths.SoundCloud_Covers, f"{filename}_cover.jpg")):
                    img_file = download_soundcloud_cover(track_url)
                else:
                    img_file = os.path.join(dirs_paths.SoundCloud_Covers, f"{filename}_cover.jpg")

                import shutil
                current_name = os.path.basename(mp3_file)
                
                if add_index_to_filename:
                    new_name = f"{str_index} {current_name}"
                else:
                    new_name = current_name
                    
                target_file_path = os.path.join(target_dir, new_name)
                
                if save_to_folder or add_index_to_filename:
                    if os.path.exists(target_file_path):
                        os.remove(target_file_path)
                    shutil.copy(mp3_file, target_file_path)
                    mp3_file = target_file_path

                if use_album_meta:
                    try:
                        try:
                            audio = mutagen.id3.ID3(mp3_file)
                        except mutagen.id3.ID3NoHeaderError:
                            audio = mutagen.id3.ID3()

                        orig_artist = str(audio.get('TPE1', entry.get('uploader', 'Unknown Author')))
                        orig_title = str(audio.get('TIT2', entry.get('title', 'Track')))
                        audio.add(mutagen.id3.TPE1(encoding=3, text=orig_artist))  
                        audio.add(mutagen.id3.TIT2(encoding=3, text=f"{str_index} {orig_title}"))
                        audio.add(mutagen.id3.TALB(encoding=3, text=playlist_unique_title))
                        audio.add(mutagen.id3.TRCK(encoding=3, text=str_index))
                        
                        if img_file and os.path.exists(img_file):
                            with open(img_file, 'rb') as f:
                                audio.add(mutagen.id3.APIC(
                                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                                ))
                        audio.save(mp3_file, v2_version=3)
                    except Exception as e:
                        print(f"Не удалось скорректировать альбомные теги: {e}")
        except Exception as trackerror:
            print(f"{trackerror}\nwith\n{track_url}")

    print(f"\nСкачивание плейлиста завершено!")
    return True
def create_soundcloud_m3u_playlist(url, music_dir=""):
    conf_file = files_paths.SoundCloud_Music_dir_conf
    
    if music_dir == "":
        if os.path.exists(conf_file) and os.path.getsize(conf_file) > 0:
            with open(conf_file, 'r', encoding='utf-8') as f:
                music_dir = f.read().strip()
        if not music_dir or music_dir.startswith("Путь к"):
            music_dir = dirs_paths.SoundCloud_Music
    else:
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(music_dir)

    try:
        with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
    except Exception:
        return None

    if not playlist_info or 'entries' not in playlist_info:
        return None

    safe_playlist_name = url_to_filename.soundcloud_playlist(url)
    
    m3u_file_path = os.path.join(dirs_paths.SoundCloud_Playlists, f"{safe_playlist_name}.m3u")
    m3u_content = f"#EXTM3U\n#PLAYLIST:{safe_playlist_name}\n"

    for entry in playlist_info['entries']:
        if not entry:
            continue
            
        track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
        if not track_url:
            continue
        filename = url_to_filename.soundcloud_track(track_url)

        full_path = os.path.normpath(os.path.join(music_dir, f"{filename}.mp3"))
        m3u_content += f"{full_path}\n"
        time.sleep(3)

    try:
        with open(m3u_file_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        return m3u_file_path
    except Exception:
        return None

def download_youtube_video_playlist(url):
    safe_playlist_name = url_to_filename.youtube_playlist(url)
    save_path = os.path.join(
        dirs_paths.Youtube_Videos, 
        "%(title)s [%(id)s].%(ext)s"
    )
    opts = ydl_opts.youtube_video_track.copy()
    opts['noplaylist'] = False
    opts['outtmpl'] = save_path
    print(f"Скачивание видео-плейлиста: {safe_playlist_name}...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
def create_youtube_m3u_playlist(url, music_dir=""):
    conf_file = files_paths.Youtube_Music_dir_conf
    
    if music_dir == "":
        if os.path.exists(conf_file) and os.path.getsize(conf_file) > 0:
            with open(conf_file, 'r', encoding='utf-8') as f:
                music_dir = f.read().strip()
        if not music_dir or music_dir.startswith("Путь к"):
            music_dir = dirs_paths.Youtube_Music
    else:
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(music_dir)

    try:
        with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
    except Exception:
        return None

    if not playlist_info or 'entries' not in playlist_info:
        return None

    safe_playlist_name = url_to_filename.youtube_playlist(url)
    
    m3u_file_path = os.path.join(dirs_paths.Youtube_Playlists, f"{safe_playlist_name}.m3u")
    m3u_content = f"#EXTM3U\n#PLAYLIST:{safe_playlist_name}\n"

    for entry in playlist_info['entries']:
        if not entry:
            continue
            
        track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
        if not track_url:
            continue

        filename = url_to_filename.youtube_track(track_url)

        full_path = os.path.normpath(os.path.join(music_dir, f"{filename}.mp3"))
        m3u_content += f"{full_path}\n"
        time.sleep(3)
        
    try:
        with open(m3u_file_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        return m3u_file_path
    except Exception:
        return None
def download_youtube_music_playlist(url, save_to_folder=True, use_album_meta=True, add_index_to_filename=True):
    with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        
    if not playlist_info or 'entries' not in playlist_info:
        print("Ошибка: Не удалось загрузить информацию о плейлисте.")
        return None
        
    playlist_title = playlist_info.get('title', 'Untitled Playlist')

    playlist_unique_title = url_to_filename.youtube_playlist_for_info(url)
    safe_name = url_to_filename.youtube_playlist(url)
    
    if save_to_folder:
        target_dir = os.path.join(dirs_paths.Youtube_Music, safe_name)
        os.makedirs(target_dir, exist_ok=True)
    else:
        target_dir = dirs_paths.Youtube_Music

    entries = list(playlist_info['entries'])
    total_tracks = len(entries)
    padding_width = len(str(total_tracks))
    playlist_title = playlist_info.get('title', 'Untitled Playlist')

    print(f"\nНачало обработки плейлиста YouTube: {playlist_title} (Всего треков: {total_tracks})")
    
    for index, entry in enumerate(entries, start=1):
        if not entry:
            continue
            
        video_id = entry.get('id') or entry.get('video_id')
        if not video_id:
            continue
            
        track_url = f"https://www.youtube.com/watch?v={video_id}"
        str_index = str(index).zfill(padding_width)
        
        try:
            filename = url_to_filename.youtube_track(track_url)
            filename = makesafename(filename)
            mp3_file = os.path.join(dirs_paths.Youtube_Music, f"{filename}.mp3")

            if os.path.exists(mp3_file):
                time.sleep(2)
            else:
                time.sleep(1)
                download_youtube_mp3(track_url)

            if mp3_file and os.path.exists(mp3_file):
                if not os.path.exists(os.path.join(dirs_paths.YoutubeMusic_Covers, f"{filename}_cover.jpg")):
                    img_file = download_youtubemusic_cover(track_url)
                else:
                    img_file = os.path.join(dirs_paths.YoutubeMusic_Covers, f"{filename}_cover.jpg")

                if use_album_meta:
                    try:
                        audio = mutagen.id3.ID3(mp3_file)
                        audio.delete()
                        audio = mutagen.id3.ID3()
                        
                        audio.add(mutagen.id3.TPE1(encoding=3, text=entry.get('uploader', 'Unknown Author')))  
                        audio.add(mutagen.id3.TIT2(encoding=3, text=playlist_unique_title))
                        audio.add(mutagen.id3.TALB(encoding=3, text=f"{playlist_title} {playlist_id}"))
                        audio.add(mutagen.id3.TRCK(encoding=3, text=str_index))
                        
                        if img_file and os.path.exists(img_file):
                            with open(img_file, 'rb') as f:
                                audio.add(mutagen.id3.APIC(
                                    encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=f.read()
                                ))
                        audio.save(mp3_file, v2_version=3)
                    except Exception as e:
                        print(f"Не удалось скорректировать альбомные теги: {e}")

                import shutil
                current_name = os.path.basename(mp3_file)
                
                if add_index_to_filename:
                    new_name = f"{str_index} {current_name}"
                else:
                    new_name = current_name
                    
                target_file_path = os.path.join(target_dir, new_name)
                
                if save_to_folder or add_index_to_filename:
                    if os.path.exists(target_file_path):
                        os.remove(target_file_path)
                    shutil.copy(mp3_file, target_file_path)

        except:
            pass
            
    print(f"\nСкачивание плейлиста завершено!")
    return True
