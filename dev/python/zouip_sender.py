import os
import subprocess
import json
import dbus
import socket
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from urllib.parse import unquote


### Get common path
current_folder = os.path.dirname(os.path.realpath(__file__))
config_filepath = os.path.join(current_folder, "zouip_config.json")

def read_json(filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset


##### INIT #####


### Get Desktop Environment specifics
# TODO Remove adb debug exception
try:
    desktop_env = os.environ['DESKTOP_SESSION']
except KeyError:
    desktop_env = "ubuntu-touch"

print("Starting Zouip Sender Daemon")

if "plasma" in desktop_env:
    print("Desktop environment supported : Plasma, proceeding")
    
    dbus_interface = "org.kde.klipper.klipper"
    dbus_member = "clipboardHistoryUpdated"
    
elif desktop_env == "ubuntu-touch":
    print("Desktop environment supported : Ubuntu Touch, proceeding")
    
    dbus_interface = "com.lomiri.content.dbus.Service"
    dbus_member = "CreatePaste"
    
else:
    print("Unsupported desktop environment, aborting")
    exit()


### Get configuration
print("Reading configuration file")
config_datas = read_json(config_filepath)

if config_datas is None:
    print("No configuration file, aborting")
    exit()
    
print(config_datas)

# Check for receivers
receiver_ids = config_datas["sender"]["receiver_ids"]

chk_active_receivers = False
for r in receiver_ids:
    if r[3]=="1":
        print(f"Active receiver found : {r[0]} on port : {r[1]}, passphrase : {r[2]}")
        chk_active_receivers = True
    else:
        print(f"Inactive receiver found : {r[0]} on port : {r[1]}, passphrase : {r[2]}")
        
if not chk_active_receivers:
    print("No active receiver found, aborting")
    exit()
    
    
### Create zouip dirs if needed
zouip_folder = config_datas["zouip_folder"]
if not os.path.isdir(zouip_folder):
    print(f"Creating zouip folder : {zouip_folder}")
    os.makedirs(zouip_folder)
else:
    print(f"Zouip folder found : {zouip_folder}")
    
old_content = None

################

def get_folder_size(folderpath):
    folder_size = 0
    for root, dirs, files in os.walk(folderpath):
        for f in files:
            folder_size += os.path.getsize(os.path.join(root, f))
    return folder_size


def get_plasma_clipboard_content():
    print("Getting plasma clipboard content")
    
    file_list = []
    
    cmd = "dbus-send --print-reply --type=method_call \
    --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents"
    
    # Format string
    byte_content = subprocess.check_output(cmd, shell=True)
    raw_content = byte_content.decode('utf-8') 
    
    start_separator = 'string "'
    start = str(raw_content).split(start_separator)[0]
    string_content = unquote(str(raw_content)[len(start)+len(start_separator):][:-2])
    
    # Get file or text
    if string_content.startswith("file://"):
        # string_content = unquote(string_content)
        file_list = string_content.split(" file://")
        file_list[0] = file_list[0].split("file://")[1]
    else:
        filepath = write_text_to_temp_file(string_content)
        file_list.append(filepath)
        
    return file_list, string_content


def get_lomiri_clipboard_content(
    args_list,
):

    print("Getting lomiri clipboard content")
    
    file_list = []
            
    # Get content from arg
    for arg in args_list:
        if str(arg).startswith("dbus.Array([dbus.Byte("):
            # print()
            # print(arg)
            raw_content = ''.join([chr(byte) for byte in arg])
            string_content = unquote(raw_content)
            
    # Get file or text
    if "text/uri-listfile:/" in string_content:
        file_content = string_content.split(r"x-special/gnome-copied-filescopy")[1]
        file_content = file_content.split("text/plainfile://")[0]
        file_content = file_content.replace(r"file://", "")
        file_list = file_content.splitlines()
        file_list.pop(0)
    else:
        text_content = string_content.split("text/plain")[1].split("text/html<!DOCTYPE HTML PUBLIC")[0]
        text_content = text_content.encode("latin1").decode()
        filepath = write_text_to_temp_file(text_content)
        file_list.append(filepath)
    
    return file_list, string_content


def get_clipboard_content(args_list):
    # Get clipboard content from DE
    if "plasma" in desktop_env:
        file_list, string_content = get_plasma_clipboard_content()
    elif desktop_env == "ubuntu-touch":
        file_list, string_content = get_lomiri_clipboard_content(args_list)
    
    # Expand folder to files only
    formatted_file_list = []

    for f in file_list:
        print(f)
        if os.path.isfile(f):
            formatted_file_list.append(
                (
                    f,
                    ".",
                    os.path.getsize(f),
                    0,
                )
            )
            
        elif os.path.isdir(f):
            basedir = os.path.basename(f)
            dir_size = get_folder_size(f)
            for root, dirs, files in os.walk(f):
                for file in files:
                    print(file)
                    formatted_file_list.append(
                        (
                            os.path.join(root, file),
                            os.path.join(
                                basedir,
                                os.path.relpath(root, f)
                            ),
                            os.path.getsize(os.path.join(root, file)),
                            dir_size,
                        )
                    )
    if file_list:
        print(f"File content : {formatted_file_list}")
        
    return formatted_file_list, string_content


def write_text_to_temp_file(
    text,
):
    
    filepath = os.path.join(config_datas["zouip_folder"], "clipboard_content.txt")
    
    print(f"Writing text content to temporary filepath : {filepath}")
        
    line_list = []
    for line in text.split(r'\n'):
        line_list.append(f"{line}\n")
        
    with open(filepath, "w") as file:
        file.writelines(line_list)

    # with open(filepath, "w") as f:
    #     f.write(text)
    #     f.close()
    
    return filepath


def _socket_send(
    host,
    port,
    request,
):

    # Check if request is not too long (>8192)
    if len(request) > 8192:
        print("Request too long (too many files), aborting")
        return False
    
    # Connect to server
    s = socket.socket()
    try:
        s.connect((host,int(port)))
    except ConnectionRefusedError:
        print(f"Unable to connect to {host}-{port}, aborting")
        return False
    
    # Send server request
    print(f"Sending request to {host}-{port} - {request}")
    s.send(request.encode())
    
    # s.sendfile(request.encode())
    
    # Get server answer
    answer = s.recv(1024).decode()
    
    # Check answer

    # Command executed
    if answer == "Executed":
        print(f"Command executed by {host}-{port}")
        s.close()
        return True
    
    # Files upload granted
    elif answer == "Granted":
        print(f"Request granted by {host}-{port}, sending content")
        s.close()
    
    # Denied or anything else
    else:
        print(f"Request denied by {host}-{port}, aborting")
        s.close()
        return False
    
    ### File Sending loop
    while True:
        
        # Connect
        s = socket.socket()
        s.connect((host,int(port)))
        
        # Wait for file request
        print("Waiting for server file request")
        request = s.recv(1024).decode()
        
        # Get request
        if request.startswith("avoid;;"):
            request = request.split("avoid;;")[1]
            remaining = int(request.split(";;")[0].split("remaining:")[1])
            filepath = request.split(";;")[1].split("file:")[1]
            
            print(f"{filepath} avoided by server, closing connection")
            s.close()
            
            # No remaining file, end
            if remaining == 0:
                break
            # Remaining file, continue
            else:
                continue
        
        remaining = int(request.split(";;")[0].split("remaining:")[1])
        filepath = request.split(";;")[1].split("file:")[1]
        
        print(f"File request received, trying to send : {filepath}")
        
        # Send file if exists
        if os.path.isfile(filepath):
            f = open(filepath, "rb", encoding=None)
            print(f"Sending file : {filepath}")
            s.sendfile(f)
            print(f"File sent : {filepath}")
        else:
            print(f"File does not exists : {filepath}")
            # Send empty packet
            s.send(b"")
        
        # Check remaining files
        print(f"Remaining files : {remaining}")
        if remaining == 0:
            print("No file remaining, closing connection")
            s.close()
            break
        
        s.close()
                    
    # Close connection
    print(f"Closing connection with {host}-{port}")
    
    return True


def build_file_request_string(
    file_list,
    passphrase,
):
    # passphrase;;files;;[file_path;;file_size;;file_subfolder]
    request_string = f"{passphrase};;files;;"
    for f in file_list:
        request_string += f"[{f[0]};;{f[1]};;{f[2]};;{f[3]}]"
    return request_string


def build_command_request_string(
    command,
    passphrase,
):
    # passphrase;;command;;<command>
    return f"{passphrase};;command;;{command}"
    
    
def dbus_monitor_loop_old(
    bus_name,
    interface_keyword,
    member_keyword,
    handler_function,
):
    
    # Get session bus
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    
    # Register signal callback
    bus.add_signal_receiver(handler_function,
                            bus_name=bus_name,
                            interface_keyword=interface_keyword,
                            member_keyword=member_keyword,
                            # path_keyword='klipper',
                            # message_keyword='msg',
                            )
    
    # Start the watch loop
    loop = GLib.MainLoop()
    loop.run()


def dbus_monitor_loop(
    match_string,
    callback_function,
):
    DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()
    bus.add_match_string_non_blocking(
        match_string
    )
    bus.add_message_filter(callback_function)

    loop = GLib.MainLoop()
    loop.run()

# def dbus_callback(*args, **kwargs):
def clipboard_dbus_callback(bus, message):
    
    # Get proper callback
    if dbus_member in str(message):
            
        print()
        print("DBUS clipboard signal detected")
        
        # for arg in message.get_args_list():
        #     print(arg)
        
        # Get clipboard content
        file_list, string_content = get_clipboard_content(message.get_args_list())

        # Send for every receiver
        global old_content
        if file_list and string_content != old_content:
            for receiver in config_datas["sender"]["receiver_ids"]:
                
                # Check if active receiver
                if receiver[3] == "1":

                    request_string = build_file_request_string(
                        file_list,
                        receiver[2],
                    )
                    
                    _socket_send(
                        receiver[0],
                        receiver[1],
                        request_string,
                    )
        else:
            print("Invalid clipboard, avoiding")            
                
        old_content = string_content

def clipboard_sender_main():

    ### DBUS

    print("Starting dbus monitoring")
    match_string = f"interface='{dbus_interface}',member='{dbus_member}',eavesdrop='true'"
    dbus_monitor_loop(
        match_string,
        clipboard_dbus_callback,
    )


# Run clipboard sender main function
clipboard_sender_main()


### SMS COMMAND TEST ###

# def send_sms_raw():
#     
#     phone_number = number.get()
#     sms_content = content.get()
#     
#     for receiver in config_datas["sender"]["receiver_ids"]:
#                     
#         # Check if active receiver
#         if receiver[3] == "1":
# 
#             request_string = build_command_request_string(
#                 f'/usr/share/ofono/scripts/send-sms /ril_0 {phone_number} "{sms_content}" 0',
#                 receiver[2],
#             )
#             
#             # print(request_string)
# 
#             _socket_send(
#                 receiver[0],
#                 receiver[1],
#                 request_string,
#             )

### SIMPLE SMS SENDER INTERFACE            
# import tkinter as tk
# 
# root = tk.Tk()
# 
# label1 = tk.Label(root, text="Phone Number : ")
# label1.pack()
# number = tk.Entry(root, show="*")
# number.pack()
# label2 = tk.Label(root, text="Content : ")
# label2.pack()
# content = tk.Entry(root)
# content.pack()
# button = tk.Button(root, text="Send", command=send_sms_raw)
# button.pack()
# 
# root.mainloop()
