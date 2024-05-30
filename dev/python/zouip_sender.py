import os, json, dbus
import dbus, dbus.proxies


# TODO
config_filepath = r"/home/tonton/Taf/zouip/dev/python/zouip_config.json"


def read_json(filepath):
    with open(filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset


def zouip_sender():
    # Get Desktop Environment specifics
    desktop_env = os.environ['DESKTOP_SESSION']

    if desktop_env == "plasmax11":
        print("Desktop Environment supported : Plasma X11")
        string = "interface='org.kde.klipper.klipper',\
        member='clipboardHistoryUpdated'"
        clipboard_cmd = "xclip -o -selection clipboard" #Dependency xclip

    elif desktop_env == "plasma":
        print("Desktop Environment supported : Plasma Wayland")
        string = "interface='org.kde.klipper.klipper',\
        member='clipboardHistoryUpdated'"
        clipboard_cmd = "wl-paste" #Dependency wayland clipboard

    elif desktop_env == "ubuntu-touch":
        print("Desktop Environment supported : Ubuntu Touch")
        string = "interface='com.lomiri.content.dbus.Service',\
        member='PasteboardChanged'"

    else:
        print("Unsupported Desktop Environment")
        return None

    config_datas = read_json(config_filepath)

    receiver_ids = config_datas["sender"]["receiver_ids"]

    if not receiver_ids:
        print("No Receiver found")
        return None

    print("Receiver found : ")
    for r in receiver_ids:
        print(f"Receiver : {r[0]} on port : {r[1]}, passphrase : {r[2]}")

    # DBUS
    # Connect to the session bus (as opposed to the system bus)
    session = dbus.SessionBus()

    #-- create proxy object of D-Bus object
    obj_proxy = dbus.proxies.ProxyObject(
        conn=session,
        bus_name="org.freedesktop.Notifications",
        object_path="/org/freedesktop/Notifications"),
    )

    # string +=",eavesdrop='true'"
    # bus.add_match_string(string)
    #
    # mainloop = gobject.MainLoop ()
    # mainloop.run ()

zouip_sender()
