from bin import interface,log,language
import os,json,pathlib

#микрофункции
def choose_from_list(choices,title=None,have_zero=False):
    if not title is None:
        print(title)
    if have_zero:
        for index in list(range(1,len(choices)))+[0]:
            print(f"[{index}] — {choices[index]}")
    else:
        for index,choice in enumerate(choices):
            print(f"[{index+1}] — {choice}")
    choice = input("> ")
    if choice.isdigit() and 1<=(int(choice)+1 if have_zero else int(choice))<=len(choices):
        choice = int(choice) if have_zero else int(choice)-1
        return {
            "index":choice,
            "text":choices[choice]
        }
    else:
        return choose_from_list(choices,title,have_zero)

#микрофункции конец

here = os.path.dirname(os.path.abspath(__file__))
listsfordownloadforfolder=os.path.join(here,"download lists")
os.makedirs(listsfordownloadforfolder,exist_ok=True)
listsfordownload = {
    "soundcloudplaylists":os.path.join(listsfordownloadforfolder,"soundcloudplaylists.json"),
    "soundcloudtracks":os.path.join(listsfordownloadforfolder,"soundcloudtracks.json")
    }
for path in listsfordownload.values():
    need_reset = False
    if not os.path.exists(path):
        need_reset = True
    else:
        try:
            with open(path, 'r', encoding='ascii') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    need_reset = True
        except Exeption:
            need_reset = True
    if need_reset:
        with open(path, 'w', encoding='ascii') as file:
                json.dump([],file,ensure_ascii=True)
music_platforms = [
    "SoundCloud"
    ]
video_platforms = [
    ]
def get_abs_or_rel(path, base=here):
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(base, path))

defaultconfiguration ={
    "lang":"en_US",
    "tracksfolder":"Music",
    "infofolder":"Info",
    "coversfolder":"Covers",
    "m3ufolder":"Playlists"
}
configuration_file = os.path.join(here,"configuration.json")
configuration = {}
def save_configuration():
    with open(configuration_file, "w", encoding="ascii") as file:
        json.dump(configuration, file, separators=(",", ":"), ensure_ascii=True)
def setlang(lang = None):
    if not lang is None:
        configuration["lang"] = lang
    language.load(configuration.get("lang",defaultconfiguration["lang"]))
def chooselanguage():
    langs = language.getlangs()
    setlang(choose_from_list(langs,language.getword("chooselanguage",{"langscount":len(langs)}))["text"])
if not os.path.exists(configuration_file) or os.path.getsize(configuration_file) == 0:
    configuration = defaultconfiguration
    setlang(defaultconfiguration["lang"])
    chooselanguage()
    save_configuration()
    log.log(language.getword("filecreated",{"file":"configuration.json"}))
else:
    with open(configuration_file, "r", encoding="ascii") as file:
        configuration = json.load(file)
    if not isinstance(configuration, dict):
        configuration = defaultconfiguration
    else:
        for key, config in defaultconfiguration.items():
            if type(configuration.get(key)) != type(config):
                configuration[index] = config
setlang()
print(language.getword("welcome"))
while True:
    choice = choose_from_list([language.getword("exit")]+[language.getword(f"option.menu.{option}") for option in range(1,4)],have_zero=True)["index"]
    if choice == 0:
        log.log(language.getword("ending"))
        break
    elif choice == 1:
        choice = choose_from_list([language.getword("exit")]+list(defaultconfiguration),language.getword("option.menu.1"),have_zero=True)
        if choice["index"] != 0:
            act = choose_from_list([language.getword("exit"),language.getword("edit"),language.getword("resettodefault"),])["index"]
            if act == 1:
                if choice["text"] == "lang":
                    chooselanguage()
                else:
                    print(choice["text"])
                    print(language.getword("pressentertokeep"))
                    inp = input()
                    if inp != "":
                        configuration[choice["text"]] = inp
            if act == 2:
                configuration[choice["text"]] = defaultconfiguration[choice["text"]]
        save_configuration()
    elif choice == 2:
        while True:
            #Создание временной переменной для конфиоурации и создание папок.
            tempconfig = {}
            for key in ["tracksfolder","infofolder","coversfolder","m3ufolder"]:
                tempconfig[key] = get_abs_or_rel(configuration[key])
                os.makedirs(tempconfig[key],exist_ok=True)
            tempconfig["playlistsinfofolder"] = os.path.join(tempconfig["infofolder"],"Playlists")
            os.makedirs(tempconfig["playlistsinfofolder"],exist_ok=True)
            #Просто создание папок.
            for platform in music_platforms:
                for key in ["tracksfolder","infofolder","playlistsinfofolder","coversfolder","m3ufolder"]:
                    os.makedirs(os.path.join(tempconfig[key],platform),exist_ok=True)
            for platform in video_platforms:
                for key in ["infofolder","coversfolder"]:
                    os.makedirs(os.path.join(tempconfig[key],platform),exist_ok=True)
            #Выбор
            choice = choose_from_list([
                language.getword("exit"),
                language.getword("dowloadplaylist",{"platform":"SoundCloud"}),
                language.getword("dowloadmusic",{"platform":"SoundCloud"})
                ],language.getword("option.menu.2"),have_zero=True)
            if choice["index"] == 0:
                break
            elif choice["index"] == 1:
                print(language.getword("dowloadoneormore"))
                if input() == "1":
                    links = []
                    with open(listsfordownload["soundcloudplaylists"], 'r', encoding='ascii') as file:
                        links = json.load(file)
                    if len(links) == 0:
                        print(language.getword("nolinksinfile"))
                        continue
                else:
                    print(language.getword("enterlinktoplaylist"))
                    links = [input()]
                print(language.getword("playlistisalbum"))
                playlistisalbum=input() == "1"
                addauthornickname = False
                if playlistisalbum:
                    print(language.getword("addauthornickname"))
                    addauthornickname=input() == "1"
                for index,link in enumerate(links):
                    log.log(language.getword("progressofdowloadingplaylists",{"progress":f"{index+1}/{len(links)}","url":link}))
                    interface.download_soundcloud_playlist(link,
                    infofolder=os.path.join(tempconfig["infofolder"],"SoundCloud"),
                    tracksfolder=os.path.join(tempconfig["tracksfolder"],"SoundCloud"),
                    coversfolder=os.path.join(tempconfig["coversfolder"],"SoundCloud"),
                    playlistsinfofolder=os.path.join(tempconfig["playlistsinfofolder"],"SoundCloud"),
                    playlistisalbum=playlistisalbum,
                    addauthornickname=addauthornickname)
            elif choice["index"] == 2:
                print(language.getword("dowloadoneormore"))
                if input() == "1":
                    links = []
                    with open(listsfordownload["soundcloudtracks"], 'r', encoding='ascii') as file:
                        links = json.load(file)
                    if len(links) == 0:
                        print(language.getword("nolinksinfile"))
                        continue
                else:
                    print(language.getword("enterlinktomusic"))
                    links = [input()]
                for index,link in enumerate(links):
                    log.log(language.getword("progressofdownloadingtracks",{"progress":f"{index+1}/{len(links)}","url":link}))
                    interface.download_soundcloud_track(link,
                    infofolder=os.path.join(tempconfig["infofolder"],"SoundCloud"),
                    tracksfolder=os.path.join(tempconfig["tracksfolder"],"SoundCloud"),
                    coversfolder=os.path.join(tempconfig["coversfolder"],"SoundCloud"))
    elif choice == 3:
        while True:
            choice = choose_from_list([language.getword("exit")]+list(listsfordownload.keys()),have_zero=True)
            if choice["index"] == 0:
                break
            else:
                path = listsfordownload[choice["text"]]
                links = []
                with open(path, 'r', encoding='ascii') as file:
                    links= json.load(file)
                while True:
                    act = choose_from_list([
                        language.getword("exit"),
                        language.getword("addlink"),
                        language.getword("removelastlink"),
                        ],f"{choice["text"]} {links[len(links)-1] if len(links) > 0 else ""}",have_zero=True)["index"]
                    if act == 0:
                        break
                    elif act == 1:
                        print(language.getword("enterlink"))
                        links.append(input())
                    elif act == 2:
                        if len(links)>0:
                            del links[-1]
                with open(path, 'w', encoding='ascii') as file:
                    json.dump(links, file, ensure_ascii=True)
                
                
save_configuration()