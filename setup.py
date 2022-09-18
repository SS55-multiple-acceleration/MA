from . import runshell

print('SETUP!\n\tsetup ffmpeg-python, yt-dlp, ffmpeg 4.x')
runshell.run('pip install ffmpeg-python')
runshell.run('pip install yt-dlp')
runshell.run('git clone https://github.com/q3aql/ffmpeg-install')
runshell.run('chmod +x ./ffmpeg-install/ffmpeg-installer.sh')
runshell.run('./ffmpeg-install/ffmpeg-installer.sh --install')
print('finish!!')