import os
import subprocess
import json
import dbus
import socket
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


def get_file_size(filepath):
    file_size = None
    if os.path.isfile(filepath):
        files_size = os.path.getsize(filepath)
    return files_size


def get_plasma_clipboard_content():
    print("Getting plasma clipboard content")
    
    file_list = []
    
    cmd = "dbus-send --print-reply --type=method_call \
    --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents"
    
    # Format string
    raw_content = subprocess.check_output(cmd, shell=True)
    start_separator = 'string "'
    start = str(raw_content).split(start_separator)[0]
    string_content = str(raw_content)[len(start)+len(start_separator):][:-3]
    
    # Get file or text
    if string_content.startswith("file://"):
        file_list = string_content.split(" file://")
        file_list[0] = file_list[0].split("file://")[1]
    else:
        filepath = write_text_to_temp_file(string_content)
        file_list.append(filepath)
        
    return file_list, string_content


def get_clipboard_content():
    if "plasma" in desktop_env:
        file_list, string_content = get_plasma_clipboard_content()
        
    if file_list:
        print(f"File content : {file_list}")
        
    return file_list, string_content


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
    file_list,
):
    
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
    
    # Get server answer
    answer = s.recv(1024).decode()
    
    # Check if answer positive
    if answer=="Denied":
        print(f"Request denied by {host}-{port}, aborting")
        s.close()
        return False
    print(f"Request granted by {host}-{port}, sending content")
    s.close()
    
    # Send files
    for filepath in file_list:
        # Connect
        s = socket.socket()
        s.connect((host,int(port)))
        
        # Send info message
        print(f"Sending {filepath} to {host}-{port}")
        file_message = f"{os.path.basename(filepath)};;0"
        s.send(file_message.encode())
        
        # Send file
        f = open(filepath, "rb", encoding=None)
        s.sendfile(f)
        
        s.close()
    
    # Close connection
    print(f"Closing connection with {host}-{port}")
    
    return True


def build_request_string(
    file_list,
    passphrase,
):
    request_string = f"{passphrase};;{len(file_list)}"
    return request_string
    
    
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
    print()
    print("DBUS clipboard signal detected")
    
    # Get clipboard content
    file_list, string_content = get_clipboard_content()
    
    # Check for empty file_list
    if not file_list:
        print("Invalid clipboard, avoiding")
        return False
    
    # Check for old call
    global old_content
    if string_content == old_content:
        print("Clipboard did not change, avoiding")
        return False
    old_content = string_content
    
    # Send for every receiver
    for receiver in config_datas["sender"]["receiver_ids"]:
        request_string = build_request_string(
            file_list,
            receiver[2],
        )
        
        _socket_send(
            receiver[0],
            receiver[1],
            request_string,
            file_list,
        )
                    
    # for i, arg in enumerate(args):
    #     print("arg:%d        %s" % (i, str(arg)))
    # print('kwargs:')
    # print(kwargs)
    # print('---end----')
    
    return True
    

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
