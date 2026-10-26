from . import applyinfo,downloader
def download_soundcloudtrack(url,infofolder=".",tracksfolder=".",coversfolder="."):
    applyinfo.set_track_tags(downloader.get_soundcloud_track(url,infofolder=infofolder,tracksfolder=tracksfolder,coversfolder=coversfolder),infofolder,tracksfolder,coversfolder)