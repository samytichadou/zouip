#!/bin/bash

port=12345

### Check desktop environment
# PlasmaX11
if [[ $DESKTOP_SESSION == "plasmax11" ]]; then
    echo "Desktop Environment supported : Plasma X11"
    clipboard_cmd="xclip -i -selection clipboard" #Dependency xclip
    notify_cmd="notify-send" #Dependency notify-send
# Plasma wayland
elif [[ $DESKTOP_SESSION == "plasma" ]]; then
    echo "Desktop Environment supported : Plasma wayland"
    clipboard_cmd="wl-copy" #Dependency wayland clipboard
    notify_cmd="notify-send" #Dependency notify-send
# Ubuntu touch
elif [[ $DESKTOP_SESSION == "ubuntu-touch" ]]; then
    echo "Desktop Environment supported : Ubuntu Touch"
else
    echo "Unsupported desktop environment"
    exit
fi

# Launch server
echo "Sarting netcat receiver server"
netcat -l -v -k $port |

# Get output
while read -r line; do
    if [[ $line != $clipboard ]];then
        clipboard=$line
        echo "$clipboard" | eval '$clipboard_cmd'
#         notify-send "Copied to clipboard : $clipboard"
        eval '$notify_cmd' "'Copied to clipboard : ${clipboard}'"
        echo "Copied to clipboard : $clipboard"
    fi
done
