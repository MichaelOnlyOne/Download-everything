import project_module

files = project_module.files_paths

config_list = [
    ("SoundCloud Music", files.SoundCloud_Music_dir_conf),
    ("Youtube Music", files.Youtube_Music_dir_conf),
    ("Video Path", files.Video_Path_Conf),
    ("Music Path", files.Music_Path_Conf),
    ("Cover Path", files.Cover_Path_Conf),
    ("Playlist Path", files.Playlist_Path_Conf)
]

while True:
    print("\n--- Меню конфигурации ---")
    print("[0] Выход")
    for i, (name, _) in enumerate(config_list, 1):
        print(f"[{i}] {name}")

    choice = project_module.inputnumber(0, len(config_list))
    
    if choice == 0:
        print("Выход из редактора.")
        break
        
    selected_name, selected_path = config_list[choice - 1]

    with open(selected_path, 'r', encoding='utf-8') as f:
        current_val = f.read().replace('\n', '')

    print(f"Текущее значение ({selected_name}): {current_val}")
    new_val = input("Введи новое значение (или Enter чтобы оставить как есть): ").replace('\r', '').replace('\n', '')

    if new_val:
        with open(selected_path, 'w', encoding='utf-8') as f:
            f.write(new_val)
        print("Сохранено.")
    else:
        print("Файл не изменен.")
