import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from urllib.parse import unquote

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
                            #path_keyword='path',
                            # message_keyword='msg',
                            # surfaceId="surfaceId"
                            #arg0="4d22da9f-18e2-4680-872f-c2b4d9ec6cc6",
                            )
    
    # Start the watch loop
    loop = GLib.MainLoop()
    loop.run()


# def dbus_callback():
def dbus_callback(*args, **kwargs):
    print()
    print("DBUS clipboard signal detected")
    print(surfaceId)
    
    # print("got signal with msg %r" % signal)
#                     
#     for i, arg in enumerate(args):
#         print("arg:%d        %s" % (i, str(arg)))
#     print('kwargs:')
#     print(kwargs)
#     print('---end----')
    
    return True
    

def zouip_sender_main():
    bus_name = "com.lomiri.content.dbus.Service"
    interface_keyword=""
    member_keyword="GetLatestPasteData"

    ### DBUS

    print("Starting dbus monitoring")
    
    # DBUS monitoring loop
    dbus_monitor_loop(
        bus_name,
        interface_keyword,
        member_keyword,
        dbus_callback,
    )

# Run main function
zouip_sender_main()
