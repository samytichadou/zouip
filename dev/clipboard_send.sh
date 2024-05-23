#!/bin/bash

host_array=(
    #ip_address:port
    0.0.0.0:12345
    192.168.1.12:12345
    192.168.1.42:12345
    192.168.1.14:12345
)

### Check desktop environment
# PlasmaX11
if [[ $DESKTOP_SESSION == "plasmax11" ]]; then
    echo "Desktop Environment supported : Plasma X11"
    interface=org.kde.klipper.klipper
    member=clipboardHistoryUpdated
    clipboard_cmd="xclip -o -selection clipboard" #Dependency xclip
# Plasma wayland
elif [[ $DESKTOP_SESSION == "plasma" ]]; then
    echo "Desktop Environment supported : Plasma wayland"
    interface=org.kde.klipper.klipper
    member=clipboardHistoryUpdated
    clipboard_cmd="wl-paste" #Dependency wayland clipboard
# Ubuntu touch
elif [[ $DESKTOP_SESSION == "ubuntu-touch" ]]; then
    echo "Desktop Environment supported : Ubuntu Touch"
    interface=com.lomiri.content.dbus.Service
    member=PasteboardChanged
else
    echo "Unsupported Desktop Environment"
    exit
fi

# Launch dbus monitor
echo "Sarting dbus monitor"
dbus-monitor --profile "interface='$interface',member='$member'" |

# Get output
while read -r line; do
    temp=$(eval "$clipboard_cmd")
    #temp=$(cmd)
    if [[ $temp != $clipboard ]]; then
        clipboard=$temp
        for key in "${host_array[@]}"
        do
            server=$( echo $key | cut -d ":" -f 1 )
            port=$( echo $key | cut -d ":" -f 2 )
            echo "$clipboard" | netcat -q0 $server $port
            echo "sent : $clipboard to : $server"
        done
    fi
done
