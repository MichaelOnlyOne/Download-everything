import project_module
def main():
    print(f"Получение ссылок из файла - {project_module.files_paths.Youtube_Music_Playlists_links}")
    urls = project_module.read_links_from_file(project_module.files_paths.Youtube_Music_Playlists_links)
    if len(urls) == 0:
        print(f"Файл с ссылкми - {project_module.files_paths.SoundCloud_Playlists_links}\nпустой")
        return
    print("Создавать m3u файл (файл плейлиста с данными) и не скачивать плейлист?")
    print("[1] - Да\n[2] - Нет")
    m3u = project_module.inputnumber(2) == 1
    if m3u:
        music_dir = input("Где ты хранишь файлы музыки? (Нажми Enter для загрузки прошлого значения из файлы)\n>")
    else:
        params = project_module.input_album_parametrs()
    for url in urls:
        try:
            if m3u:
                project_module.create_youtube_m3u_playlist(url,music_dir)
            else:
                project_module.download_youtube_music_playlist(url,params)
        except:
            print(f"Что то пошло не так с {url}")
main()