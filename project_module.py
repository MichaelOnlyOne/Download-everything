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
        'format': 'bestaudio/best',
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
    return safe_name

class url_to_filename:
    @staticmethod
    def youtube_video(url):
        try:
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Untitled Video')
            v_id = info.get('id', 'unknown_id')
            return makesafename(f"{video_title} [{v_id}]")
        except Exception:
            return "youtube_video"
    @staticmethod
    def youtube_track(url):
        log_file = None
        try:
            log_file = open(files_paths.log, "a", encoding="utf-8")
            log_file.write(f"[START] Получен URL: {url}\n")
            log_file.flush()
            with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
                info = ydl.extract_info(url, download=False)
            v_id = info.get('id', 'unknown_id')
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
            return makesafename(f"{video_title} [{video_id}]")
        except Exception:
            return "rutube_video"


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
            return makesafename(f"{playlist_id} {playlist_title}")
        except Exception:
            return "soundcloud_playlist"


def download_soundcloud_cover(url, filename=None):
    if filename is None:
        filename = url_to_filename.soundcloud_track(url)

    filename = makesafename(filename)
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        info = ydl.extract_info(url, download=False)
    img_url = info.get('thumbnail')
    
    if img_url:
        full_path = os.path.join(dirs_paths.SoundCloud_Covers, f"{filename}_cover.jpg")
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
def download_youtube_cover(url, filename=None):
    if filename is None:
        filename = url_to_filename.youtube_video(url)

    filename = makesafename(filename)

    with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
        info = ydl.extract_info(url, download=False)
    img_url = info.get('thumbnail')
    
    if img_url:
        full_path = os.path.join(dirs_paths.Youtube_Covers, f"{filename}_cover.jpg")
        try:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            img.save(full_path, 'JPEG')
            print(f"Обложка YouTube сохранена: {full_path}")
            return full_path
        except Exception as e:
            print(f"Не удалось обработать обложку YouTube: {e}")
    return None
def download_youtubemusic_cover(url, filename=None):
    if filename is None:
        filename = url_to_filename.youtube_video(url)
    filename = makesafename(filename)

    full_path = os.path.join(dirs_paths.YoutubeMusic_Covers, f"{filename}_cover.jpg")
    os.makedirs(dirs_paths.YoutubeMusic_Covers, exist_ok=True)

    img_file = download_youtube_cover(url, filename)
    
    if img_file and os.path.exists(img_file):
        try:
            import numpy as np
            with Image.open(img_file) as img:
                img = img.convert("RGB")
                width, height = img.size
                
                if width > height:
                    img_np = np.array(img)
                    crop_needed = width - height
                    left_margin = crop_needed // 2
                    right_margin = width - (crop_needed - left_margin)
                    
                    left_zone = img_np[:, :left_margin]
                    right_zone = img_np[:, right_margin:]
                    
                    is_left_empty = np.std(left_zone) < 15
                    is_right_empty = np.std(right_zone) < 15
                    
                    if is_left_empty and is_right_empty:
                        img_final = img.crop((left_margin, 0, right_margin, height))
                    else:
                        bg_color = img.getpixel((0, 0)) 
                        img_final = Image.new("RGB", (width, width), bg_color)
                        img_final.paste(img, (0, (width - height) // 2))
                else:
                    img_final = img
                
                img_final.save(full_path, "JPEG", quality=95)
                print(f"Обложка обработана и сохранена в YoutubeMusic_Covers: {full_path}")
                return full_path
        except Exception as e:
            print(f"Не удалось обработать и сохранить обложку: {e}")
            
    return None

def download_rutube_video(url, filename=None):
    if filename is None:
        filename = url_to_filename.rutube_video(url)
    filename = makesafename(filename)
    
    save_path = os.path.join(dirs_paths.Rutube_Videos, f"{filename}.%(ext)s")
    opts = ydl_opts.rutube_video_track
    opts['outtmpl'] = save_path
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
def download_youtube_video(url, filename=None):
    if filename is None:
        filename = url_to_filename.youtube_video(url)

    filename = makesafename(filename)

    save_path = os.path.join(dirs_paths.Youtube_Videos, f"{filename}.%(ext)s")
    
    opts = ydl_opts.youtube_video_track
    opts['outtmpl'] = save_path
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def download_soundcloud_mp3(url,SavePath=dirs_paths.SoundCloud_Music, filename=None):
    if filename is None:
        filename = url_to_filename.soundcloud_track(url)
    print(filename)
    filename = makesafename(filename)

    save_path = os.path.join(SavePath, f"{filename}.%(ext)s")
    
    opts = ydl_opts.soundcloud_audio_track
    opts['outtmpl'] = save_path
    
    print(f"Скачивание MP3 с SoundCloud: {filename}...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
        return os.path.join(os.path.join(SavePath, f"{filename}.mp3"))
    return None
def download_youtube_mp3(url,SavePath=dirs_paths.Youtube_Music, filename=None):
    if filename is None:
        filename = url_to_filename.youtube_track(url)

    filename = makesafename(filename)

    save_path = os.path.join(SavePath, f"{filename}.%(ext)s")
    
    opts = ydl_opts.youtube_audio_track.copy()
    opts['outtmpl'] = save_path
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        predicted_path = ydl.prepare_filename(info_dict)
        final_mp3_path = os.path.splitext(predicted_path)[0] + '.mp3'
        ydl.download([url])
        return final_mp3_path
        
    return None

def download_soundcloud_track_with_info(url,SavePath=dirs_paths.SoundCloud_Music, custom_filename=None):
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        info = ydl.extract_info(url, download=False)
    
    try:
        if custom_filename is not None:
            filename = custom_filename
        else:
            filename = url_to_filename.soundcloud_track(url)
    except Exception:
        filename = "soundcloud_track"
    download_soundcloud_mp3(url,SavePath, filename)
    mp3_file = os.path.join(SavePath, f"{filename}.mp3")
    
    if not os.path.exists(mp3_file):
        print(f"Ошибка: MP3 файл {mp3_file} SoundCloud не был создан.")
        return None

    img_file = download_soundcloud_cover(url, filename)
    
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
    ''' 
    if img_file and os.path.exists(img_file):
        os.remove(img_file)
    '''
    return mp3_file
def download_youtube_track_with_info(url,SavePath=dirs_paths.Youtube_Music, custom_filename=None):
    with yt_dlp.YoutubeDL(ydl_opts.youtube_info) as ydl:
        info = ydl.extract_info(url, download=False)
        
    video_id = info.get('id', 'unknown_id')
    
    try:
        if custom_filename is not None:
            filename = custom_filename
        else:
            filename = url_to_filename.youtube_track(url)
            
        filename = makesafename(filename)
    except Exception:
        filename = "youtube_track"

    mp3_file = download_youtube_mp3(url,SavePath, filename)
    
    if mp3_file is None or not os.path.exists(mp3_file):
        print("Ошибка: MP3 файл YouTube не был создан.")
        return None

    img_file = download_youtubemusic_cover(url, filename)
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
    '''
    if img_file and os.path.exists(img_file):
        os.remove(img_file)
    '''
    return mp3_file


def download_soundcloud_playlist(url, save_to_folder=True, use_album_meta=True, add_index_to_filename=True):
    with yt_dlp.YoutubeDL(ydl_opts.soundcloud_info) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        
    if not playlist_info or 'entries' not in playlist_info:
        print("Ошибка: Не удалось загрузить информацию о плейлисте.")
        return None
        
    playlist_title = playlist_info.get('title', 'Untitled Playlist')
    playlist_id = str(playlist_info.get('id', 'unknown_id'))
    if ":" in playlist_id:
        import re
        match = re.search(r'\b\d{5,}\b', playlist_id)
        playlist_id = match.group(0) if match else playlist_id.replace(':', '-')
   
    safe_name = url_to_filename.soundcloud_playlist(url)
    
    if save_to_folder:
        target_dir = os.path.join(dirs_paths.SoundCloud_Music, safe_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
    else:
        target_dir = dirs_paths.SoundCloud_Music


    entries = list(playlist_info['entries'])
    total_tracks = len(entries)
    padding_width = len(str(total_tracks))

    print(f"\nНачало обработки плейлиста: {playlist_title} (Всего треков: {total_tracks})")
    
    for index, entry in enumerate(entries, start=1):
        time.sleep(1)
        try:
            if not entry:
                continue
                
            track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
            if not track_url:
                continue
                
            str_index = str(index).zfill(padding_width)
            
            mp3_file = download_soundcloud_track_with_info(track_url,target_dir)

            if mp3_file and os.path.exists(mp3_file):
                if add_index_to_filename:
                    current_name = os.path.basename(mp3_file)
                    new_name = f"{str_index} {current_name}"
                    new_file_path = os.path.join(target_dir, new_name)
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    os.rename(mp3_file, new_file_path)
                    mp3_file = new_file_path

                if use_album_meta:
                    try:
                        audio = mutagen.id3.ID3(mp3_file)
                        actual_title = audio.get('TIT2').text[0] if audio.get('TIT2') else "Track"
                        
                        audio.add(mutagen.id3.TIT2(encoding=3, text=f"{str_index} {actual_title}"))
                        audio.add(mutagen.id3.TALB(encoding=3, text=f"{playlist_title} {playlist_id}"))
                        audio.add(mutagen.id3.TRCK(encoding=3, text=str_index))
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

        # ИСПОЛЬЗУЕМ ЗДЕСЬ: получаем имя трека через класс без ручной нарезки URL
        filename = url_to_filename.soundcloud_track(track_url)

        full_path = os.path.normpath(os.path.join(music_dir, f"{filename}.mp3"))
        m3u_content += f"{full_path}\n"

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
        safe_playlist_name, 
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
    playlist_id = playlist_info.get('id', 'unknown_id')
    
    # Получаем имя плейлиста через созданный класс для YouTube
    safe_name = url_to_filename.youtube_playlist(url)
    
    if save_to_folder:
        target_dir = os.path.join(dirs_paths.Youtube_Music, safe_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
    else:
        target_dir = dirs_paths.Youtube_Music

    entries = list(playlist_info['entries'])
    total_tracks = len(entries)
    padding_width = len(str(total_tracks))

    print(f"\nНачало обработки плейлиста YouTube: {playlist_title} (Всего треков: {total_tracks})")
    
    for index, entry in enumerate(entries, start=1):
        if not entry:
            continue
            
        track_url = entry.get('url') or entry.get('webpage_url') or entry.get('url_transparent')
        if not track_url:
            continue
            
        str_index = str(index).zfill(padding_width)
        
        try:
            mp3_file = download_youtube_track_with_info(track_url, target_dir)

            if mp3_file and os.path.exists(mp3_file):
                if add_index_to_filename:
                    current_name = os.path.basename(mp3_file)
                    new_name = f"{str_index} {current_name}"
                    new_file_path = os.path.join(target_dir, new_name)
                    
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    os.rename(mp3_file, new_file_path)
                    mp3_file = new_file_path

                if use_album_meta:
                    try:
                        audio = mutagen.id3.ID3(mp3_file)
                        actual_title = audio.get('TIT2').text[0] if audio.get('TIT2') else "Track"
                        
                        audio.add(mutagen.id3.TIT2(encoding=3, text=f"{str_index} {actual_title}"))
                        audio.add(mutagen.id3.TALB(encoding=3, text=f"{playlist_title} {playlist_id}"))
                        audio.add(mutagen.id3.TRCK(encoding=3, text=str_index))
                        audio.save(mp3_file, v2_version=3)
                    except Exception as e:
                        print(f"Не удалось скорректировать альбомные теги: {e}")
        except:
            pass
            
    print(f"\nСкачивание плейлиста завершено!")
    return True
