import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

interface = "org.kde.klipper.klipper"
member = "clipboardHistoryUpdated"

def nf(bus, message):
    # while True:
    #     if not member in message:
    #         continue
    print(message)
    if member in str(message):
        print("yeah")
        args = message.get_args_list()
        for arg in message.get_args_list():
            print('arg:' + str(arg))

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking(
    # "member='clipboardHistoryUpdated'"
    "interface='org.kde.klipper.klipper',eavesdrop='true',member='clipboardHistoryUpdated'"
    # "interface=com.lomiri.content.dbus.Service,eavesdrop='true',member='GetLatestPasteData'"
    # "eavesdrop='true',member='GetLatestPasteData'"
)
bus.add_message_filter(nf)

loop = GLib.MainLoop()
loop.run()
