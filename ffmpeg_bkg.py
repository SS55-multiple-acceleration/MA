import random
from . import runshell

def make_bkg(out_w, out_h, color=None, out_path=None):
    if out_path == None:
        out_path = 'bkg.png'
    if color == None:
        color_list = ('black', 'white', 'pink', 'red', 'green', 'yellow', 'blue', 'purple')
        color = random.choice(color_list)
    cmd = f"ffmpeg -loglevel error -y -f lavfi -i color=c={color}:s={int(out_w)}x{int(out_h)}:sar=1/1 -vframes 1 {out_path}"
    runshell.run(cmd)
    return out_path