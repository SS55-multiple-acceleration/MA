import ffmpeg
from . import runshell
from . import get_info

def error_check(stream):
    try:
        _ = stream.overwrite_output().run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

def initialize_video(input_video, in_w, in_h, aspectfill=False, output_video=None) ->str:
    '''動画をイニシャライズする。

    Arguments:
        input_video(str): 入力動画のパス
        in_w(int): 出力動画の横長さ
        in_h(int): 出力動画の縦長さ
        aspectfill(bool): 出力動画を、AspectFillするかどうか。Falseなら、ScaleToFitつまり引き延ばされる。
        output_video(str): 出力動画のパス

    return: 
        出力動画のパス(str)
    '''
    if output_video == None:
        output_video = 'input.mp4'
    print(f'''\n動画を初期化する
    \tinput: {input_video}
    \tin_w: {in_w}
    \tin_h: {in_h}
    \toutput: {output_video}''')
    if aspectfill == True:
        cmd = f'ffmpeg -loglevel error -y -i {input_video} -vf scale={int(in_w)}:{int(in_h)}:force_original_aspect_ratio=increase,crop={int(in_w)}:{int(in_h)},fps=60 -af aresample=48000 -r 60 -ar 48000 -vcodec libx264 -preset ultrafast {output_video}'
    else:
        cmd = f'ffmpeg -loglevel error -y -i {input_video} -vf scale={int(in_w)}:{int(in_h)},fps=60 -af aresample=48000 -r 60 -ar 48000 -vcodec libx264 -preset ultrafast {output_video}'
    runshell.run(cmd)
    return output_video
    
# def force_4_3(input_video, in_h, output_video=None) ->str:
#     '''動画を4:3にコンバートする。

#     Arguments:
#         input_video(str): 入力動画のパス
#         in_h(int): 出力動画の縦長さ
#         output_video(str): 出力動画のパス

#     return: 
#         出力動画のパス(str)
#     '''
#     if output_video == None:
#         output_video = 'input4_3.mp4'
#     print(f'''\n動画を初期化する
#     \tinput: {input_video}
#     \tin_h: {in_h}
#     \toutput: {output_video}''')
#     in_w = in_h * 4 // 3
#     cmd = f'ffmpeg -loglevel error -y -i {input_video} -vf scale={int(in_w)}:{int(in_h)},force_original_aspect_ratio=increase,crop={int(in_w)}:{int(in_h)},fps=60 -af aresample=48000 -r 60 -ar 48000 -vcodec libx264 -preset ultrafast {output_video}'
#     runshell.run(cmd)
#     return output_video

def convert_MA_tile(bkg_path, video_path, a, b, output_path=None, color=None, peak_time=None, speed_lambda=None, start_lambda=None, rainbow=False, rainbow_saturation=1, rainbow_flick=10):
    '''タイル状の多重加速動画を作る

    Arguments: 
        bkg_path(str): 背景の画像のパス(必要ないかも)
        video_path(str): 入力動画のパス
        a(int): 出力動画の縦に並ぶ動画の数
        b(int): 出力動画の横に並ぶ動画の数
        output_path(str): 出力動画のパス
        color(str): 基本の色
        peak_time(float):
        speed_lambda(function):
        start_lambda(function):
        rainbow(bool):  
    
    Returns:
        出力動画のパス(str)
        
    '''
    in0 = ffmpeg.input(bkg_path)
    split = ffmpeg.input(video_path).split()
    split_audio = ffmpeg.input(video_path).filter_multi_output('asplit')
    color = 'black' if color == None else color
    print(f'''\nタイル状・多重加速動画を生成する
    \tinput_bkg: {bkg_path}
    \tinput_video: {video_path}
    \toutput: {output_path}''', end='')
    video_duration = get_info.get_duration(video_path)

    if peak_time == None:
        peak_time = get_info.get_duration(video_path)
        print(f'\n\tpeak_time: {peak_time}', end='')
    if peak_time > video_duration:
        peak_tie = get_info.get_duration(video_path)
        print(f'\n\tpeak_time: {peak_time} * peak_timeが動画長さより長かったため,peak_timeを動画長さ({peak_time}s)に補正', end='')
    if start_lambda == None and speed_lambda == None:
        start_lambda = lambda i: peak_time / (a * b) * (i)
        print(f'\n\tstart_lambda: {start_lambda}', end='')
    if speed_lambda == None:
        speed_lambda = lambda i: peak_time * (1 / (peak_time - start_lambda(i)))
        print(f'\n\tspeed_lambda: {speed_lambda}', end='')
    if start_lambda == None:
        start_lambda = lambda i: peak_time * (1 - 1 / speed_lambda(i))
        print(f'\n\tstart_lambda: {start_lambda}', end='')

    start_time = start_lambda
    speed = speed_lambda
    rainbow_01 = int(rainbow)
    
    in_w, in_h = get_info.get_width_height(video_path)

    for i in range(a * b):
        in1 = (
            split[i]
            .filter('setpts', f'PTS/{speed(i):.3f}')
            .filter('hue', h=f'{start_time(i) * rainbow_01} + {rainbow_flick} * {speed(i) * rainbow_01} * n', s=f'{rainbow_saturation}')
            .filter('tpad', start_duration=f'{start_time(i):.3f}', color=color)
            .filter('tpad', stop=1, color=color)
        )
        in0 = ffmpeg.filter([in0, in1], 'overlay', in_w * (i % b), in_h * (i // b))
    video_stream = in0

    audio_elem = []
    for i in range(a * b):
        audio_elem.insert(0, 
            split_audio[i]
            .filter('asetrate', f'48000*{speed(i):.3f}')
            .filter('aresample', '48000')
            .filter('adelay', delays=f'{start_time(i)*1000:.3f}S', all='1')
        )

    audio_stream = (
                    ffmpeg
                    .filter(audio_elem, 'amix', inputs = f'{a * b}')
                    .filter('volume', f'{a * b}dB')
    )

    stream = ffmpeg.output(video_stream, audio_stream, 
                        output_path, 
                        vcodec = 'libx264', 
                        preset = 'ultrafast')

    error_check(stream)
    return output_path

def finalize_360video(video_path, title, artist, date_today, ydl_url, out_video_path, codec='libx264'):
    metadata_dict = {"metadata:g:0": f"title={title}", 
                    "metadata:g:1": f"artist={artist}", 
                    "metadata:g:2": f"date={date_today}", 
                    "metadata:g:3": f"""description=SSが作成したVR空間作成ツールにて生成
                    Google Colabにてエンコード : https://colab.research.google.com
                    original : {ydl_url}"""}

    out_video_path = out_video_path.replace(' ', '_')
    print(f'''\n360度動画をファイナライズする
    \tinput: {video_path}
    \ttitle: {title}
    \tdate_today: {date_today}
    \toutput: {out_video_path}''')

    video_stream = ffmpeg.input(video_path).filter('v360', input='c3x2', in_forder='frbldu', output='equirect')
    audio_stream = ffmpeg.input(video_path).audio
    stream = (
        ffmpeg.output(video_stream, audio_stream, 
                f'{out_video_path}', 
                vcodec = codec, 
                preset = 'ultrafast',
                **metadata_dict)
    )
    error_check(stream)
    return out_video_path


def finalize_video(video_path, title, artist, date_today, ydl_url, out_video_path, codec='libx264'):
    metadata_dict = {"metadata:g:0": f"title={title}", 
                    "metadata:g:1": f"artist={artist}", 
                    "metadata:g:2": f"date={date_today}", 
                    "metadata:g:3": f"""description=SSが作成したVR空間作成ツールにて生成
                    Google Colabにてエンコード : https://colab.research.google.com
                    original : {ydl_url}"""}

    out_video_path = out_video_path.replace(' ', '_')
    print(f'''\n動画をファイナライズする
    \tinput: {video_path}
    \ttitle: {title}
    \tdate_today: {date_today}
    \toutput: {out_video_path}''')

    video_stream = ffmpeg.input(video_path)
    audio_stream = ffmpeg.input(video_path).audio
    stream = (
        ffmpeg.output(video_stream, audio_stream, 
                f'{out_video_path}', 
                vcodec = codec, 
                preset = 'ultrafast',
                **metadata_dict)
    )
    error_check(stream)
    return out_video_path
