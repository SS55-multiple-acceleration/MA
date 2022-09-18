import datetime
from . import setup
from . import videodownload
from . import get_info
from . import ffmpeg_bkg
from . import convert_video

def MultipleAcceleration360(title=None, ydl_url=None, aspectfill=False, a=None, b=None, base_pixel=None, peak_time=None, speed_lambda=None, start_lambda=None, codec='libx264'):
    print('''55 Auto VR Multiple Acceralation Generater:
    \t入力の動画をタイル状に多重加速して、それを上下左右前後に敷き詰めた360°動画にするぞ\n''')

    title = input('動画のタイトルを入力 ->') if title == None else title
    ydl_url = input('元動画のURLを入力 ->') if ydl_url == None else ydl_url
    base_pixel = int(input('画質を入力 (例 4K:2160 FHD:1080, HD:720) ->')) if base_pixel == None else base_pixel
    peak_time = float(input('多重加速のピークを入力してください(seconds) ->')) if peak_time == None else peak_time

    date_today = datetime.date.today().strftime('%Y/%m/%d')
    artist = '55 Auto VR MultipleAcceleration Generater'
    video_path = videodownload.video_download(ydl_url)
    a, b = get_info.get_aspect(video_path) if (a == None or b == None) else a, b
    # if aspectfill == True:
    #     a = 4 if a == None else a
    #     b = 4 if b == None else b
    #     a, b = a, b
    # else:
    #     a, b = get_info.get_aspect(video_path)
    print(f'\n*) 画面比率は、{a}:{b}')

    out_w, out_h = base_pixel, base_pixel
    in_w, in_h = int(out_w / b), int(out_h / a)
    in_w, in_h = in_w + (in_w % 2), in_h + (in_h % 2)

    color = 'black'
    bkg_path = ffmpeg_bkg.make_bkg(out_w, out_h, color, out_path='/content/bkg.png')
    video_path = convert_video.initialize_video(video_path, in_w, in_h, aspectfill, '/content/initialized.mp4')
    square_video_path = convert_video.convert_MA_tile(bkg_path, video_path, a, b, '/content/sauqred.mkv', color=color, peak_time=peak_time, speed_lambda=speed_lambda, start_lambda=start_lambda)

    a, b = 2, 3
    bkg2_path = ffmpeg_bkg.make_bkg(out_w * b, out_h * a, color, out_path='/content/bkg2.png')
    tiled_video_path = convert_video.convert_MA_tile(bkg2_path, square_video_path, a, b, '/content/tiled.mkv', color=color, peak_time=peak_time, speed_lambda=speed_lambda, start_lambda=start_lambda)

    out_video_path = f'./{title}.mp4'
    convert_video.finalize_360video(tiled_video_path, title, artist, date_today, ydl_url, out_video_path, codec)
    print('finish!')


def MultipleAccelerationStandard(title=None, ydl_url=None, base_pixel=None, a=None, b=None, peak_time=None, speed_lambda=None, start_lambda=None, rainbow=False, rainbow_saturation=1, rainbow_flick=1, codec='libx264'):
    print('''55 Auto Multiple Acceralation Generater:
    \t入力の動画をタイル状に多重加速して、動画にするぞ\n''')

    title = input('動画のタイトルを入力 ->') if title == None else title
    ydl_url = input('元動画のURLを入力 ->') if ydl_url == None else ydl_url
    base_pixel = int(input('画質を入力 (例 4K:2160 FHD:1080, HD:720) ->')) if base_pixel == None else base_pixel
    peak_time = float(input('多重加速のピークを入力してください(seconds) ->')) if peak_time == None else peak_time
    a = int(input('多重加速の縦の動画数を入力してください（例: 4 -> 最終動画に、縦に4つの動画が並ぶ）')) if a == None else a
    b = int(input('多重加速の横の動画数を入力してください（例: 4 -> 最終動画に、横に4つの動画が並ぶ）')) if b == None else b 
    
    date_today = datetime.date.today().strftime('%Y/%m/%d')
    artist = '55 Auto MultipleAcceleration Generater'
    video_path = videodownload.video_download(ydl_url)
    aspect_b, aspect_a = get_info.get_aspect(video_path)

    out_w, out_h = base_pixel * (aspect_b / aspect_a), base_pixel
    in_w, in_h = int(out_w / b), int(out_h / a)
    in_w, in_h = in_w + (in_w % 2), in_h + (in_h % 2)

    color = 'black'
    bkg_path = ffmpeg_bkg.make_bkg(out_w, out_h, color, out_path='/content/bkg.png')
    video_path = convert_video.initialize_video(video_path, in_w, in_h, '/content/initialized.mp4')
    square_video_path = convert_video.convert_MA_tile(bkg_path, video_path, a, b, '/content/sauqred.mkv', color=color, peak_time=peak_time, speed_lambda=speed_lambda, start_lambda=start_lambda, rainbow=rainbow, rainbow_saturation=rainbow_saturation, rainbow_flick=rainbow_flick)

    out_video_path = f'./{title}.mp4'
    convert_video.finalize_video(square_video_path, title, artist, date_today, ydl_url, out_video_path, codec)
    print('finish!')

if __name__ == '__main__':
    MultipleAccelerationStandard(title=None, ydl_url=None, base_pixel=None, peak_time=None, speed_lambda=None, start_lambda=None, codec='libx265')