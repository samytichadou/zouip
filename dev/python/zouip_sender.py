import os
import subprocess
import json
import dbus
import time
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop


def read_json(filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset


##### INIT #####


### Get Desktop Environment specifics
desktop_env = os.environ['DESKTOP_SESSION']

print("Starting Zouip Sender Daemon")

if "plasma" in desktop_env:
    print("Desktop environment supported : Plasma, proceeding")
    
    bus_name = "org.kde.klipper"
    interface_keyword="klipper"
    member_keyword="clipboardHistoryUpdated"
    
elif desktop_env == "ubuntu-touch":
    print("Desktop environment supported : Ubuntu Touch, proceeding")
    
    bus_name = "org.kde.klipper"
    interface_keyword="klipper"
    member_keyword="clipboardHistoryUpdated"

else:
    print("Unsupported desktop environment, aborting")
    exit()


### Get configuration
print("Reading configuration file")
current_folder = os.path.dirname(os.path.realpath(__file__))
config_filepath = os.path.join(current_folder, "zouip_config.json")
config_datas = read_json(config_filepath)

if config_datas is None:
    print("No configuration file, aborting")
    exit()
    
print(config_datas)

receiver_ids = config_datas["sender"]["receiver_ids"]

if not receiver_ids:
    print("No Receiver found, aborting")
    exit()

for r in receiver_ids:
    print(f"Receiver found : {r[0]} on port : {r[1]}, passphrase : {r[2]}")
    
    
### Create zouip dirs if needed
zouip_folder = config_datas["zouip_folder"]
if not os.path.isdir(zouip_folder):
    print(f"Creating zouip folder : {zouip_folder}")
    os.makedirs(zouip_folder)
else:
    print(f"Zouip folder found : {zouip_folder}")
    
old_content = None

################


def build_handshake_command(
    receiver_datas,
    text_content = "", 
    files_content = [],
):
    # passphrase;;type;;file01_name;;file02_name (if files)
    
    string = f"{receiver_datas[3]};;"
    
    if text_content:
        string += "text"
    elif files_content:
        string += "files"
        for filepath in files_content:
            filename = os.path.basename(filepath)
            string += f";;{filename}"
    else:
        return None
    
    handhsake_cmd = f" echo '{string}' | netcat -q0 {receiver_datas[0]} {receiver_datas[1]}"
    
    return handhsake_cmd


def get_files_size(file_list):
    files_size = 0
    for filepath in file_list:
        if os.path.isfile(filepath):
            files_size += os.path.getsize(filepath)
    return files_size


def get_plasma_clipboard_content():
    print("Getting plasma clipboard content")
    
    text_content = None
    file_list = []
    
    cmd = "dbus-send --print-reply --type=method_call \
    --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents"

    raw_content = subprocess.check_output(cmd, shell=True)
    string_content = str(raw_content).split('string "')[1].split(r'"\n')[0]
    
    if string_content.startswith("file://"):
        file_list = string_content.split(" file://")
        file_list[0] = file_list[0].split("file://")[1]
    else:
        text_content = string_content
        
    return text_content, file_list, string_content


def get_clipboard_content():
    if "plasma" in desktop_env:
        text_content, file_list, string_content = get_plasma_clipboard_content()
        
    if text_content:
        print(f"Text content : {text_content}")
    else:
        print(f"File content : {file_list}")
        
    return text_content, file_list, string_content


def write_text_to_temp_file(
    text,
):
    
    filepath = os.path.join(config_datas["zouip_folder"], "clipboard_temp.txt")
    
    print(f"Writing text content to temporary filepath : {filepath}")
    
    line_list = []
    for line in text.split(r'\n'):
        line_list.append(f"{line}\n")
        
    with open(filepath, "w") as file:
        file.writelines(line_list)
    
    return filepath


def send_clipboard_content(
    text_content,
    file_list,
    receiver,
):
    
    print("Sending clipboard content")
    netcat_cmd = f" | netcat {receiver[0]} {receiver[2]} -q0"

    # Text content
    if text_content:
        
        # Store in file
        filepath = write_text_to_temp_file(text_content)
        file_list.append(filepath)
        
    # Files content
    if file_list:
        
        for filepath in file_list:
            
            send_cmd = f"cat {filepath}{netcat_cmd}"
            print(f"Sending command : {send_cmd}")
            subprocess.call(send_cmd, shell=True)
    
    return True
        


def dbus_monitor_loop(
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

def dbus_callback(*args, **kwargs):
    # TODO Prevent double call
    print()
    print("DBUS clipboard signal detected")
    
    # Get clipboard content
    text_content, file_list, string_content = get_clipboard_content()
    
    # Check for old call
    global old_content
    if string_content == old_content:
        print("Clipboard did not change, avoiding")
        return False
    old_content = string_content

    # Check if limit size
    if not text_content and file_list:
        print("Getting files size")
        files_size = get_files_size(file_list)
        if files_size > config_datas["sender"]["size_limit"]:
            print(f"Files size superior to size limit ({files_size}>{config_datas['sender']['size_limit']}), avoiding")
            return False
        else:
            print(f"Files size inferior to size limit ({files_size}<{config_datas['sender']['size_limit']}), proceeding")
    
    # Send for every receiver
    for receiver in config_datas["sender"]["receiver_ids"]:
        
        # Build handshake command for every receivers
        print(f"Building command handshake to {receiver[0]}-{receiver[1]}")
        cmd = build_handshake_command(
            receiver,
            text_content,
            file_list,
        )
        
        if cmd is None:
            print(f"Invalid content to send to {receiver[0]}-{receiver[1]}, avoiding")
            return False
        
        print(f"Sending command handshake to {receiver[0]}-{receiver[1]} : {cmd}")
        subprocess.call(cmd, shell=True)
        
        # Send clipboard content
        send_clipboard_content(
            text_content,
            file_list,
            receiver,
        )
    
    # for i, arg in enumerate(args):
    #     print("arg:%d        %s" % (i, str(arg)))
    # print('kwargs:')
    # print(kwargs)
    # print('---end----')
    

def zouip_sender_main():

    ### DBUS

    print("Starting dbus monitoring")
    
    # DBUS monitoring loop
    dbus_monitor_loop(
        bus_name,
        interface_keyword,
        member_keyword,
        dbus_callback,
    )
            
    # Connect to the session bus (as opposed to the system bus)
    # session = dbus.SessionBus()
    # 
    # #-- create proxy object of D-Bus object
    # obj_proxy = dbus.proxies.ProxyObject(
    #     conn=session,
    #     bus_name="org.freedesktop.Notifications",
    #     object_path="/org/freedesktop/Notifications"),
    # )

    # string +=",eavesdrop='true'"
    # bus.add_match_string(string)
    #
    # mainloop = gobject.MainLoop ()
    # mainloop.run ()


# Run main function
zouip_sender_main()
