import dbus


### PLASMA
item = "org.freedesktop.Notifications"

notfy_intf = dbus.Interface(
    dbus.SessionBus().get_object(item, "/"+item.replace(".", "/")), item)

# (	app_name, 	 
#  	replaces_id, 	 
#  	app_icon, 	 
#  	summary, 	 
#  	body, 	 
#  	actions, 	 
#  	hints, 	 
#  	expire_timeout);	

notfy_intf.Notify(
    "Title",
    0,
    "",
    "Object",
    "Body",
    [],
    {"urgency": 1},
    10000,
)

### LOMIRI
# on https://askubuntu.com/questions/755556/persistent-notification-on-ubuntu-touch
# (need the application with proper push settings)

# gdbus call --session --dest com.ubuntu.Postal \
# --object-path /com/ubuntu/Postal/com_2eubuntu_2edeveloper_2ewebapps_2ewebapp_2dtwitter \
# --method com.ubuntu.Postal.Post \
# com.ubuntu.developer.webapps.webapp-twitter_webapp-twitter \
# "\"{\\\"message\\\": \\\"foobar\\\", \\\"notification\\\":{\\\"card\\\": {\\\"summary\\\": \\\"Some Title\\\", \\\"body\\\": \\\"Some text\\\", \\\"popup\\\": true, \\\"persist\\\": true}}}\""
