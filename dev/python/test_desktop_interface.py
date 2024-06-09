send_to_list= [
    {
        "name": "FP4",
        "address": "192.168.1.12",
        "port": 12345,
        "passphrase": "azerty",
        "active": 1,
        "clipboard_type": "text"
    },
    {
        "name": "FP4",
        "address": "192.168.1.12",
        "port": 12345,
        "passphrase": "azerty",
        "active": 1,
        "clipboard_type": "text"
    },
]
    
command_list = [
    {
        "name": "command1"
    },
    {
        "name": "command2"
    },
    {
        "name": "command3"
    },
]

import tkinter as tk
from tkinter import filedialog

### Commands
def _on_receive_button_toggle():
    if receive_var.get():
        print("receive_button is on")
    else:
        print("receive_button is off")
        
def _on_send_button_toggle():
    if receive_var.get():
        print("send is on")
    else:
        print("send_button is off")
        
def _zouip_folder_button():
    foldername = filedialog.askdirectory()
    zouip_folder.set(foldername)
    print(f"zouip_folder : {foldername}")
    
def command_popup(button):
     try:         
        x = button.winfo_rootx()
        y = button.winfo_rooty()
        popup.tk_popup(x, y, 0)
     finally:
           popup.grab_release()
    
### UI
window = tk.Tk()

# Set geometry
window.geometry("500x600")
window.resizable(True, True)

### Theming
# Set padding
window['padx'] = 20
window['pady'] = 20
# Set theme
# bg_color = "#1B1E20"
# window.configure(bg = bg_color)
window.title("Zouip")
# window.grid_rowconfigure(0, weight=0)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)

row = 0

### Zouip state
state_label = tk.Label(
    window,
    text="Zouip State",
).grid(row=row, column=0, sticky="w")

# Receive toggle
receive_var = tk.IntVar()
receive_var.set(0)
receive_button = tk.Checkbutton(
    window,
    text="Receive",
    variable=receive_var,
    command=_on_receive_button_toggle,
).grid(row=row, column=1, sticky="w")

# Send toggle
send_var = tk.IntVar()
send_var.set(0)
send_button = tk.Checkbutton(
    window,
    text="Send",
    variable=send_var,
    command=_on_send_button_toggle,
).grid(row=row, column=2, sticky="e")

row += 1

# Spacer
tk.Label(window, text="").grid(row=row, column=0)

row += 1

### Settings
settings_label = tk.Label(
    window,
    text="Settings",
).grid(row=row, column=0, sticky="w")

row += 1

# Zouip folder
zouip_folder = tk.StringVar()
zouip_folder_label = tk.Label(
    window,
    text="Zouip Folder",
).grid(row=row, column=0, sticky="w")
zouip_folder_entry = tk.Entry(
    window,
    textvariable=zouip_folder,
    # width=40,
).grid(row=row, column=1, sticky="we")
zouip_folder_button = tk.Button(
    text="Browse",
    command=_zouip_folder_button,
).grid(row=row, column=2, sticky="e")

row += 1

# Receive port
# TODO accept only numeric input
receive_port = tk.IntVar()
receive_port.set(12345)
receive_port_label = tk.Label(
    window,
    text="Receive Port",
).grid(row=row, column=0, sticky="w")
receive_port_entry = tk.Entry(
    window,
    textvariable=receive_port,
).grid(row=row, column=1, sticky="we",columnspan=2)

row += 1

# Size limit
size_limit = tk.IntVar()
size_limit_label = tk.Label(
    window,
    text="Receive Size Limit",
).grid(row=row, column=0, sticky="w")
size_limit_entry = tk.Entry(
    window,
    textvariable=size_limit,
).grid(row=row, column=1, sticky="we",columnspan=2)

row += 1

# Passphrase
# TODO
passphrase_button = tk.Button(
    window,
    text="Change Passphrase",
).grid(row=row, column=0, sticky="w")

# Keep Files
keep_files = tk.IntVar()
keep_files.set(1)
keep_files_button = tk.Checkbutton(
    window,
    text="Keep Files",
    variable=keep_files,
).grid(row=row, column=1)

# Copy to clipboard
copy_to_clipboard = tk.IntVar()
copy_to_clipboard.set(0)
copy_to_clipboard_button = tk.Checkbutton(
    window,
    text="Copy to Clipboard",
    variable=copy_to_clipboard,
).grid(row=row, column=2)
row += 1

# Save
save_settings_button = tk.Button(
    text="Save Settings",
).grid(row=row, column=0, sticky="we", columnspan=3)


# Spacer
row += 1
tk.Label(window, text="").grid(row=row, column=0)
row += 1

# Send to list
size_limit_label = tk.Label(
    window,
    text="Send To",
).grid(row=row, column=0, sticky="w")
row += 1
list_items = tk.Variable(
    value=[x["name"] for x in send_to_list],
)
send_list = tk.Listbox(
    window,
    listvariable=list_items,
    height=len(send_to_list),
).grid(row=row, column=0, sticky="we",columnspan=3)

# Command submenu
popup = tk.Menu(window, tearoff=0)
for command in command_list:
    popup.add_command(
        label=command["name"],
    )
    
row += 1

# Command button
command_button = tk.Button(
    window,
    text="Send Command",
    command=lambda: command_popup(command_button),
)
command_button.grid(row=row, column=0)

# Modify button
modify_send_button = tk.Button(
    window,
    text="Modify",
).grid(row=row, column=1)

row += 1

### Run
window.mainloop()
