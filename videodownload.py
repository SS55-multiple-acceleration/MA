'''動画のダウンロード'''
import os
import glob
from yt_dlp import YoutubeDL
from . import runshell

def video_download(ydl_url):
    '''YouTubeからの動画のダウンロード

    Attributes:
        ydl_url(str): 動画のURLs

    Returns: 
        None
    '''
    
    dl_path = '/content/download.*'

    dl_path_pre = dl_path.replace('.', '_pre.')
    ydl_opts = {
        'format': 'best', 
        'outtmpl': dl_path_pre.replace('*', '%(ext)s')}
    print(f'''\n動画のダウンロード
    \tYT_DLP: download {ydl_url} -> {dl_path_pre}''')
    if len(glob.glob(dl_path_pre)) > 0:
        os.remove(glob.glob(dl_path_pre)[0])
    with YoutubeDL(ydl_opts) as ydl:
        x = ydl.download([ydl_url])
    runshell.run(f'ffmpeg -y -i {dl_path_pre} -vcodec libx264 -preset ultrafast {dl_path.replace("*", "mp4")}')
    return dl_path.replace("*", "mp4")


if __name__=='__main__':
    ydl_url = input('動画をダウンロードします。URLを入力 ->')
    video_download(ydl_url)