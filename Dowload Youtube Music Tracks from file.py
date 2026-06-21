import project_module
music_dir = ""
def main():
    print(f"Получение ссылок из файла - {project_module.files_paths.Youtube_Music_links}")
    urls = project_module.read_links_from_file(project_module.files_paths.Youtube_Music_links)
    for url in urls:
        print(url)
        try:
            project_module.download_youtube_track_with_info(url)
        except:
            print(f"Что то пошло не так с {url}")
main()