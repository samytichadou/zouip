import os
import json
import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop


def read_json(filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset

### Set global variables
# TODO
current_folder = os.path.dirname(os.path.realpath(__file__))
config_filepath = os.path.join(current_folder, "zouip_config.json")
config_datas = read_json(config_filepath)


def build_handshake_command(
    receiver_datas,
    text_content = "", 
    files_content = [],
):
    
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
    print("Clipboard change detected")
    
    for r in config_datas["sender"]["receiver_ids"]:
        print(f"Handshake to {r[0]}-{r[1]}")
        # Handshake
        print(f"Sending to {r[0]}-{r[2]}")
        # Send file
    
    # for i, arg in enumerate(args):
    #     print("arg:%d        %s" % (i, str(arg)))
    # print('kwargs:')
    # print(kwargs)
    # print('---end----')
    

def zouip_sender_main():
    ### Get Desktop Environment specifics
    
    desktop_env = os.environ['DESKTOP_SESSION']
    
    print("Starting Zouip Sender Daemon")

    if desktop_env == "plasmax11":
        print("Desktop Environment supported : Plasma X11")
        
        bus_name = "org.kde.klipper"
        interface_keyword="klipper"
        member_keyword="clipboardHistoryUpdated"

        clipboard_cmd = "xclip -o -selection clipboard" #Dependency xclip

    elif desktop_env == "plasma":
        print("Desktop Environment supported : Plasma Wayland")
        
        bus_name = "org.kde.klipper"
        interface_keyword="klipper"
        member_keyword="clipboardHistoryUpdated"
        
        clipboard_cmd = "wl-paste" #Dependency wayland clipboard

    elif desktop_env == "ubuntu-touch":
        print("Desktop Environment supported : Ubuntu Touch")
        
        bus_name = "org.kde.klipper"
        interface_keyword="klipper"
        member_keyword="clipboardHistoryUpdated"

    else:
        print("Unsupported Desktop Environment")
        return None
    
    ### Get configuration
    
    print("Reading configuration file")
    config_datas = read_json(config_filepath)
    
    if config_datas is None:
        print("No configuration file, aborting")
        return None

    receiver_ids = config_datas["sender"]["receiver_ids"]

    if not receiver_ids:
        print("No Receiver found, aborting")
        return None

    print("Receiver found : ")
    for r in receiver_ids:
        print(f"Receiver : {r[0]} on port : {r[1]}, passphrase : {r[2]}")

    ### DBUS

    print("Starting dbus monitoring")
    
    # DBUS monitoring loop
    dbus_monitor_loop(
        bus_name,
        interface_keyword,
        member_keyword,
        dbus_callback,
    )
    # TODO Prevent double call
    
    # Fake callback
    while True:
        
        # Get clipboard content on change
        clipboard_text = ""
        clipboard_files = [
            "/home/tonton/Taf/UBUNTU_TOUCH/zouip/README.md",
            "/home/tonton/Taf/UBUNTU_TOUCH/zouip/LICENSE",
        ]
        
        # Check if limit size
        if not clipboard_text and clipboard_files:
            print("Getting files size")
            files_size = get_files_size(clipboard_files)
            if files_size > config_datas["sender"]["size_limit"]:
                print(f"Files size superior to size limit ({files_size}>{config_datas['sender']['size_limit']}), avoiding")
                continue
            else:
                print(f"Files size inferior to size limit ({files_size}<{config_datas['sender']['size_limit']}), proceeding")

        # Build handshake command for every receivers
        for r in receiver_ids:
            cmd = build_handshake_command(
                r,
                clipboard_text,
                clipboard_files,
            )
            
            if cmd is None:
                print(f"Invalid content to send to {r[0]}-{r[1]}, avoiding")
                continue

            print(cmd)
        
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
