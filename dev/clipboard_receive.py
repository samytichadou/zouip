import os
import time
import subprocess

print("--- start listening")

file = r"/home/tonton/Desktop/fairphone/heard.out"

if not os.path.isfile(file):
    old = 0
else:
    old = os.path.getsize(file)

while True:

    time.sleep(1)

    if not os.path.isfile(file):
        if old:
            old = 0
        continue

    if os.path.getsize(file)!=old:
        with open(file) as f:
            for line in f:
                pass
            if line:
                last_line = line
            else:
                continue

        clipboard = last_line[:-1]
        print(f"New input : {clipboard}")
        cmd = f'echo "{clipboard}" | xclip -i -selection clipboard'
        subprocess.Popen(cmd, shell=True)
        cmd = f'notify-send "Copied to clipboard : {clipboard}"'
        subprocess.Popen(cmd, shell=True)
        old = os.path.getsize(file)
