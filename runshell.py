import subprocess
from subprocess import PIPE

def run(cmd):
    print(f'Runsh_cmd...({cmd})')
    subprocess.run(cmd,shell=True,stdout=PIPE,stderr=PIPE,text=True)