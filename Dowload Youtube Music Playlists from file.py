import project_module
music_dir = ""
def main():
    print(f"Получение ссылок из файла - {project_module.files_paths.Youtube_Music_Playlists_links}")
    urls = project_module.read_links_from_file(project_module.files_paths.Youtube_Music_Playlists_links)
    Params = [False,False,False,False]
    if len(urls) == 0:
        print(f"Файл с ссылкми - {project_module.files_paths.SoundCloud_Playlists_links}\nпустой")
        return
    print("Создавать m3u файл (файл плейлиста с данными) и не скачивать плейлист?")
    print("[1] - Да\n[2] - Нет")
    Params[3] = project_module.inputnumber(2) == 1
    if Params[3]:
        music_dir = input("Где ты хранишь файлы музыки? (Нажми Enter для загрузки прошлого значения из файлы)\n>")
    else:
        print("Сохранить в отдельную папку плейлиста?")
        print("[1] - Да\n[2] - Нет")
        Params[0] = project_module.inputnumber(2) == 1
        if Params[0]:    
            print("Добавить в начале названия каждого файла идекс порядка в плейлиста?")
            print("[1] - Да\n[2] - Нет")
            Params[1] = project_module.inputnumber(2) == 1
            print("Указать в название альбома плейлист?")
            print("[1] - Да\n[2] - Нет")
            Params[2] = project_module.inputnumber(2) == 1
    for url in urls:
        print(url)
        try:
            if Params[3]:
                project_module.create_youtube_m3u_playlist(url,music_dir)
            else:
                project_module.download_youtube_music_playlist(url,Params[0],Params[1],Params[2])
        except:
            print(f"Что то пошло не так с {url}")
main()