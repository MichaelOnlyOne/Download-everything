import project_module
from spotdl import SpotDL

# Инициализируем клиент (можно передать настройки, например, формат)
spotdl = SpotDL(args={"format": "mp3"})

# Ссылка на трек, альбом или плейлист Spotify
spotify_url = "https://open.spotify.com/track/1y4eO1DftiwKMD5YAELgmx"

try:
    # 1. Ищем трек и собираем метаданные со Spotify
    print("Ищем трек и собираем данные...")
    songs = spotdl.search([spotify_url])
    
    # 2. Скачиваем песню через движок yt-dlp (ищет совпадение на YouTube)
    print(f"Скачиваем: {songs[0].name} - {songs[0].artist}")
    spotdl.download_songs(songs)
    print("Загрузка успешно завершена!")

except Exception as e:
    print(f"Произошла ошибка: {e}")
