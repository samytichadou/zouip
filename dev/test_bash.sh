#!/bin/bash

# array=(
#     "192.168.1.0 12345"
#     192.168.2.0
# )
# echo ${array[0]}
# echo ${array[1]}
# echo
#
# for key in "${array[@]}"
# do
#     echo $key | cut -d " " -f 1
#     echo $key | cut -d " " -f 2
# #     while read -r word1 word2; do
# #         echo "$word1"
# #         echo "$word2"
# #     done
#   echo "Key for fruits array is: $key"
# done

# echo
# declare -a bigarray
#
# bigarray[0]=(
#     0.0.0.0
#     12345
# )
# bigarray[1]=(
#     0.0.0.0
#     98765
# )
#
# for key in "${bigarray[@]}"
# do
#     echo ${key[0]}
#     echo ${key[1]}
# done

# notif_cmd="notify-send"
# text="test"
# eval '$notif_cmd' "'lalala - ${text}'"

# set clipboard
# set_clipboard_command="dbus-send --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents"
# content="heigf"
# eval '$set_clipboard_command' string:"$content"
# dbus-send --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:"$content"

# get clipboard
# dbus-send --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents
# server=$( echo $key | cut -d ":" -f 1 )
# test=$( dbus-send --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents )
# echo $test
# #test=$( echo $test | cut -d 'string "' -f 2 )
# echo $(grep -oP 'string/"\s+\K\w+' $test)
# echo $test
#echo ${test::-1} #remove last character of string
array=( t e s t )
echo $array | base64
# printf "gAwo/KOGx6InYAsv5Qt8rhHshtO/H75HG+iYJ+GdcqodUHpbjQ==" | base64 -c -d | xxd -p -c 1000

