import dbus
import time
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

def dbus_callback(*args, **kwargs):
    print("Clipboard change detected")
    
    # for i, arg in enumerate(args):
    #     print("arg:%d        %s" % (i, str(arg)))
    # print('kwargs:')
    # print(kwargs)
    # print('---end----')

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

dbus_monitor_loop(
    'org.kde.klipper',
    'klipper',
    'clipboardHistoryUpdated',
    dbus_callback,
    )
