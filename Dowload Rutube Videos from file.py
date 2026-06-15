import project_module
print(f"Получение ссылок из файла - {project_module.files_paths.Rutube_Videos_links}")
urls = project_module.read_links_from_file(project_module.files_paths.Rutube_Videos_links)
if len(urls) == 0:
    print(f"Файл с ссылкми - {project_module.files_paths.Rutube_Videos_links}\nпустой")
for url in urls:
    print(url)
    try:
        project_module.download_rutube_video(url)
    except:
        print(f"Что то пошло не так с {url}")