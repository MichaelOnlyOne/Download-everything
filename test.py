import project_module
for url in ["https://soundcloud.com/after_f/sets/lyublyu-syurrealizm","https://soundcloud.com/discover/sets/personalized-tracks::after_f:1942342307","https://soundcloud.com/discover/sets/your-moods:1696833782:8"]:
    print(url,end = " ")
    print(project_module.url_to_filename.soundcloud_playlist(url))