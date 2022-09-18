import glob
import ffmpeg
import math

def get_aspect(video_path) ->tuple:
    video_path = glob.glob(video_path)[0]
    qualitys = get_width_height(video_path)
    gcd = math.gcd(*qualitys)
    a, b = [int(i / gcd) for i in qualitys]
    return a, b

def get_width_height(video_path) ->tuple:
    w = ffmpeg.probe(video_path)['streams'][0]['coded_width']
    h = ffmpeg.probe(video_path)['streams'][0]['coded_height']
    return w, h

def get_duration(video_path) ->int:
    duration = float(ffmpeg.probe(video_path)['format']['duration'])
    return duration