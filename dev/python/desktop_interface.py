import tkinter as tk
from tkinter import filedialog, Toplevel

import json
import os

def get_zouip_config_file():
    home_folder = os.environ['HOME']
    config_folder = os.path.join(home_folder, ".config")
    zouip_config_folder = os.path.join(config_folder, "zouip")
    return os.path.join(zouip_config_folder,"zouip_config.json")

def get_config_datas():
    zouip_config_file = get_zouip_config_file()
    
    # Existing file
    if os.path.isfile(zouip_config_file):
        with open(zouip_config_file, "r") as read_file:
            config_datas = json.load(read_file)
            
    # No config file
    else:
        config_datas = {
            "zouip_folder": "",
            "receive_port": 0,
            "passphrase": "",
            "size_limit": 0,
            "keep_files": 1,
            "copy_to_clipboard": 0,
            "receive_from_list": [],
            "send_to_list": []
        }
        
    return config_datas

def save_json(filepath, datas):
    # Create folder if needed
    basedir = os.path.dirname(filepath)
    os.makedirs(basedir, exist_ok=True)
    
    # Save json
    with open(filepath, "w", encoding='utf8') as write_file :
        json.dump(datas, write_file, indent=4, sort_keys=False)


class Zouip_main_window(tk.Frame):
    
    def open_main_settings(self):
        if self.main_settings_window is not None:
            try:
                self.main_settings_window.state()
                print("Already opened window")
                return
            except tk.TclError:
                pass
        self.main_settings_window = Toplevel()#self.parent)
        Zouip_main_settings_parent(self.main_settings_window)
        print("Opening main settings window")
        
    def open_receive_from_settings(self):
        if self.receive_settings_window is not None:
            try:
                self.receive_settings_window.state()
                print("Already opened window")
                return
            except tk.TclError:
                pass
        self.receive_settings_window = Toplevel()
        Zouip_receive_from_settings_parent(self.receive_settings_window)
        print("Opening receive from settings window")
        
    def open_send_to_settings(self):
        if self.send_settings_window is not None:
            try:
                self.send_settings_window.state()
                print("Already opened window")
                return
            except tk.TclError:
                pass
        self.send_settings_window = Toplevel()
        Zouip_send_to_settings_parent(self.send_settings_window)
        print("Opening send to settings window")
    
    def on_receive_button_toggle(self): #TODO
        if self.receive_toggle_variable.get():
            print("receive is on")
        else:
            print("receive is off")
            
    def on_send_button_toggle(self): #TODO
        if self.send_toggle_variable.get():
            print("send is on")
        else:
            print("send is off")
    
    def refresh_window(self):
        # Get previous state
        receive = self.receive_toggle_variable.get()
        send = self.send_toggle_variable.get()
        
        # Refresh
        self.destroy()
        self.__init__(self.parent)
        
        # Set state from previous
        self.receive_toggle_variable.set(receive)
        self.send_toggle_variable.set(send)
        
        print("Window refreshed")
        
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Set setting windows variables
        self.main_settings_window = None
        self.receive_settings_window = None
        self.send_settings_window = None
        
        # Set variables
        self.receive_toggle_variable = tk.IntVar()
        self.send_toggle_variable = tk.IntVar()
        
        # Refresh settings
        self.datas = get_config_datas()

        # Set geometry
        parent.geometry("500x300")
        parent.resizable(True, True)
        parent.title("Zouip")

        ### Theming
        # Set padding
        parent['padx'] = 20
        parent['pady'] = 20
        # parent.grid_rowconfigure(0, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        row = 0
        
        # Main settings
        settings_button = tk.Button(
            text="Main Settings",
            command=self.open_main_settings,
        ).grid(row=row, column=0, sticky="w")
        
        # Receive from settings
        receive_from_settings_button = tk.Button(
            text="Receive from Settings",
            command=self.open_receive_from_settings,
        ).grid(row=row, column=1, sticky="we")
        
        # Send to settings
        send_to_settings_button = tk.Button(
            text="Send to Settings",
            command=self.open_send_to_settings,
        ).grid(row=row, column=2, sticky="e")

        row += 1
        
        # Separator
        tk.Label(text="").grid(row=row)#, column=2, sticky="e")
        row += 1
        
        ### Zouip state
        state_label = tk.Label(
            parent,
            text="Zouip State",
        ).grid(row=row, column=0, sticky="w")

        # Receive toggle
        receive_toggle_button = tk.Checkbutton(
            parent,
            text="Receive",
            variable=self.receive_toggle_variable,
            command=self.on_receive_button_toggle,
        ).grid(row=row, column=1, sticky="e")

        # Send toggle
        send_toggle_button = tk.Checkbutton(
            parent,
            text="Send",
            variable=self.send_toggle_variable,
            command=self.on_send_button_toggle,
        ).grid(row=row, column=2, sticky="e")
        row += 1
        
        # Separator
        tk.Label(text="").grid(row=row)#, column=2, sticky="e")
        row += 1
        
        # Refresh Window
        refresh_settings_button = tk.Button(
            parent,
            text="Refresh",
            command=self.refresh_window,
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        ### Send to list
        for item in self.datas['send_to_list']:
            tk.Label(
                parent,
                text=item["name"],
            ).grid(row=row, column=0, sticky="we", columnspan=3)
            
            # TODO Activate/Deactivate toggle
            # TODO Send command
            
            row += 1


class Zouip_main_settings_parent(tk.Frame):
    
    def refresh_settings(self):
        self.datas = get_config_datas()
        
        self.zouip_folder.set(self.datas["zouip_folder"])
        self.receive_port.set(self.datas["receive_port"])
        self.passphrase.set(self.datas["passphrase"])
        self.size_limit.set(self.datas["size_limit"])
        self.keep_files.set(self.datas["keep_files"])
        self.copy_to_clipboard.set(self.datas["copy_to_clipboard"])
        print("Settings refreshed")
        
    def save_settings(self):
        # Check for valid save
        if not self.zouip_folder.get()\
        or not self.receive_port.get()\
        or not self.passphrase.get():
            tk.messagebox.showerror("Error", "Invalid Entry")
            print("Invalid selection, avoiding save")
            return
        
        # Set datas
        self.datas["zouip_folder"] = self.zouip_folder.get()
        self.datas["receive_port"] = self.receive_port.get()
        self.datas["passphrase"] = self.passphrase.get()
        self.datas["size_limit"] = self.size_limit.get()
        self.datas["keep_files"] = self.keep_files.get()
        self.datas["copy_to_clipboard"] = self.copy_to_clipboard.get()
        
        # Save json
        save_json(get_zouip_config_file(), self.datas)
            
        print("Settings saved")
        
    def _zouip_folder_button(self):
        folderpath = filedialog.askdirectory(
            initialdir = self.zouip_folder.get(),
            title = "Zouip Folder",
        )
        if folderpath:
            self.zouip_folder.set(folderpath)
            print(f"zouip_folder : {folderpath}")
        
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Set settings variables
        self.zouip_folder = tk.StringVar()
        self.receive_port = tk.IntVar()
        self.passphrase = tk.StringVar()
        self.size_limit = tk.IntVar()
        self.keep_files = tk.IntVar()
        self.copy_to_clipboard = tk.IntVar()
        
        self.refresh_settings()

        # Set geometry
        parent.geometry("500x300")
        parent.resizable(True, True)
        parent.title("Zouip Main Settings")

        ### Theming
        # Set padding
        parent['padx'] = 20
        parent['pady'] = 20
        # parent.grid_rowconfigure(0, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        row = 0
        
        # Config folder informations
        config_folder_label = tk.Label(
            parent,
            text="Config folder : /home/username/.config/zouip/",
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        # Refresh Settings
        refresh_settings_button = tk.Button(
            parent,
            text="Refresh Settings",
            command=self.refresh_settings,
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1

        ### Zouip folder
        tk.Label(
            parent,
            text="Zouip Folder",
        ).grid(row=row, column=0, sticky="w")
        zouip_folder_entry = tk.Entry(
            parent,
            textvariable=self.zouip_folder,
        ).grid(row=row, column=1, sticky="we")
        zouip_folder_button = tk.Button(
            parent,
            text="Browse",
            command=self._zouip_folder_button,
        ).grid(row=row, column=2, sticky="e")
        row += 1

        ### Receive port
        # TODO accept only numeric input
        tk.Label(
            parent,
            text="Receive Port",
        ).grid(row=row, column=0, sticky="w")
        receive_port_entry = tk.Entry(
            parent,
            textvariable=self.receive_port,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1

        # Passphrase
        tk.Label(
            parent,
            text="Passphrase",
        ).grid(row=row, column=0, sticky="w")
        passphrase_entry = tk.Entry(
            parent,
            textvariable=self.passphrase,
            show="*",
        ).grid(row=row, column=1, sticky="we", columnspan=2)
        row += 1

        # Size limit
        tk.Label(
            parent,
            text="Receive Size Limit",
        ).grid(row=row, column=0, sticky="w")
        size_limit_entry = tk.Entry(
            parent,
            textvariable=self.size_limit,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Misc
        tk.Label(
            parent,
            text="Miscellaneous",
        ).grid(row=row, column=0, sticky="w")
        # Keep Files
        self.keep_files.set(1)
        keep_files_button = tk.Checkbutton(
            parent,
            text="Keep Files",
            variable=self.keep_files,
        ).grid(row=row, column=1, sticky="w")

        # Copy to clipboard
        self.copy_to_clipboard.set(0)
        copy_to_clipboard_button = tk.Checkbutton(
            parent,
            text="Copy to Clipboard",
            variable=self.copy_to_clipboard,
        ).grid(row=row, column=2)
        row += 1
        
        # Save
        save_settings_button = tk.Button(
            parent,
            text="Save Settings",
            command=self.save_settings,
        ).grid(row=row, column=0, sticky="we", columnspan=3)

        
class Zouip_receive_from_settings_parent(tk.Frame):
    
    def remove_entry(self):
        # Check for invalid selection
        if self.current_receive_from.get() in {"New entry", "None"}:
            print("Invalid selection, avoiding remove")
            tk.messagebox.showerror("Error", "Invalid Entry")
            return
        
        # Ask user confirmation
        confirm = tk.messagebox.askyesno("Warning", "Are you sure ?")
        if not confirm:
            print("Cancelled by user, avoiding")
            return
        
        # Remove selected entry
        selected = self.datas["receive_from_list"][self.current_index]
        del (self.datas["receive_from_list"][self.current_index])
        
        # Save json
        save_json(get_zouip_config_file(), self.datas)
        
        # Refresh settings
        self.refresh_settings()
            
        print("Entry removed, saved")
    
    def get_selected_receive_from(self, event):
        # No selection
        if not self.receive_from_list.curselection():
            print("no selection")
            return
        
        # Set index
        index = self.receive_from_list.curselection()[0]
        self.current_index = index
        
        # Set variables according to selection
        # New entry
        if self.receive_from_list.get(index) == "New entry":
            self.name_variable.set("")
            self.address_variable.set("")
            self.clipboard_variable.set("both")
            self.current_receive_from.set("New entry")
        # Existing entry
        else:
            selected = self.datas["receive_from_list"][index]
            self.name_variable.set(selected["name"])
            self.address_variable.set(selected["address"])
            self.clipboard_variable.set(selected["clipboard_type"])
            self.current_receive_from.set(selected["name"])
        
        print("Receiver from refreshed")
    
    def refresh_settings(self):
        self.datas = get_config_datas()
        
        temp_list = [x["name"] for x in self.datas["receive_from_list"]]
        temp_list.append("New entry")
        
        self.list_items.set(temp_list)
        print("Settings refreshed")
        
    def save_settings(self):
        # New entry
        if self.current_receive_from.get() == "New entry":
            if not self.name_variable.get()\
            or not self.address_variable.get():
                tk.messagebox.showerror("Error", "Invalid Entry")
                print("Invalid selection, avoiding save")
                return
                
            new_entry = {}
            new_entry["name"] = self.name_variable.get()
            new_entry["address"] = self.address_variable.get()
            new_entry["active"] = 1
            new_entry["clipboard_type"] = self.clipboard_variable.get()
            self.datas["receive_from_list"].append(new_entry)
            print("Entry created")
            
        # Modify existing
        elif self.current_receive_from.get() != "None":
            
            if not self.name_variable.get()\
            or not self.address_variable.get():
                tk.messagebox.showerror("Error", "Invalid Entry")
                print("Invalid selection, avoiding save")
                return
            
            selected = self.datas["receive_from_list"][self.current_index]
            
            selected["name"] = self.name_variable.get()
            selected["address"] = self.address_variable.get()
            selected["clipboard_type"] = self.clipboard_variable.get()
            print("Entry modified")
        
        # Invalid entry
        else:
            tk.messagebox.showerror("Error", "Invalid Entry")
            print("Invalid selection, avoiding save")
            return
        
        # Set new entry name
        self.current_receive_from.set(self.name_variable.get())
        
        # Save json
        save_json(get_zouip_config_file(), self.datas)
        
        # Refresh settings
        self.refresh_settings()
            
        print("Settings saved")
        
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Set variables
        self.current_receive_from = tk.StringVar()
        self.current_receive_from.set("None")
        self.current_index = -1
        self.name_variable = tk.StringVar()
        self.address_variable = tk.StringVar()
        self.clipboard_variable = tk.StringVar()
        self.list_items = tk.Variable()
        
        self.refresh_settings()

        # Set geometry
        parent.geometry("500x400")
        parent.resizable(True, True)
        parent.title("Zouip Receive from Settings")

        ### Theming
        # Set padding
        parent['padx'] = 20
        parent['pady'] = 20
        # parent.grid_rowconfigure(0, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        row = 0
        
        # Config folder informations
        config_folder_label = tk.Label(
            parent,
            text="Config folder : /home/username/.config/zouip/",
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        # Refresh Settings
        refresh_settings_button = tk.Button(
            parent,
            text="Refresh Settings",
            command=self.refresh_settings,
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        ### Receive from list_items
        
        self.receive_from_list = tk.Listbox(
            parent,
            listvariable=self.list_items,
            height=5,
        )
        self.receive_from_list.grid(row=row, column=0, sticky="we",columnspan=3)
        self.receive_from_list.bind("<<ListboxSelect>>", self.get_selected_receive_from)
        row += 1
        
        ### Settings
        
        # Current selection
        tk.Label(
            parent,
            text = "Selected : ",
        ).grid(row=row, column=0, sticky="w")
        tk.Label(
            parent,
            textvariable = self.current_receive_from,
        ).grid(row=row, column=1, sticky="w")
        row += 1
        
        # Name
        name_label = tk.Label(
            parent,
            text = "Name",
        ).grid(row=row, column=0, sticky="w")
        name_entry = tk.Entry(
            parent,
            textvariable = self.name_variable,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Address
        address_label = tk.Label(
            parent,
            text = "Address",
        ).grid(row=row, column=0, sticky="w")
        address_entry = tk.Entry(
            parent,
            textvariable = self.address_variable,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Clipboard type
        clipboard_button0 = tk.Radiobutton(
            parent,
            text="Text and Files",
            variable=self.clipboard_variable,
            value="both",
        ).grid(row=row, column=0, sticky="w")
        clipboard_button1 = tk.Radiobutton(
            parent,
            text="Text",
            variable=self.clipboard_variable,
            value="text",
        ).grid(row=row, column=1, sticky="w")
        clipboard_button2 = tk.Radiobutton(
            parent,
            text="Files",
            variable=self.clipboard_variable,
            value="file",
        ).grid(row=row, column=2, sticky="w")
        row += 1
        
        ### Save
        save_settings_button = tk.Button(
            parent,
            text="Save Entry Settings",
            command=self.save_settings,
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        ### Remove entry
        remove_entry_button = tk.Button(
            parent,
            text="Remove entry",
            command=self.remove_entry,
        ).grid(row=row, column=0, sticky="we", columnspan=3)


class Zouip_send_to_settings_parent(tk.Frame):
    
    def remove_entry(self):
        # Check for invalid selection
        if self.current_send_to.get() in {"New entry", "None"}:
            print("Invalid selection, avoiding remove")
            tk.messagebox.showerror("Error", "Invalid Entry")
            return
        
        # Ask user confirmation
        confirm = tk.messagebox.askyesno("Warning", "Are you sure ?")
        if not confirm:
            print("Cancelled by user, avoiding")
            return
        
        # Remove selected entry
        selected = self.datas["send_to_list"][self.current_index]
        del (self.datas["send_to_list"][self.current_index])
        
        # Save json
        save_json(get_zouip_config_file(), self.datas)
        
        # Refresh settings
        self.refresh_settings()
            
        print("Entry removed, saved")
    
    def get_selected_send_to(self, event):
        # No selection
        if not self.send_to_list.curselection():
            print("no selection")
            return
        
        # Set index
        index = self.send_to_list.curselection()[0]
        self.current_index = index
        
        # Set variables according to selection
        # New entry
        if self.send_to_list.get(index) == "New entry":
            self.name_variable.set("")
            self.address_variable.set("")
            self.port_variable.set(0)
            self.passphrase_variable.set("")
            self.clipboard_variable.set("both")
            self.current_send_to.set("New entry")
        # Existing entry
        else:
            selected = self.datas["send_to_list"][index]
            self.name_variable.set(selected["name"])
            self.address_variable.set(selected["address"])
            self.port_variable.set(selected["port"])
            self.passphrase_variable.set(selected["passphrase"])
            self.clipboard_variable.set(selected["clipboard_type"])
            self.current_send_to.set(selected["name"])
        
        print("Receiver from refreshed")
    
    def refresh_settings(self):
        self.datas = get_config_datas()
        
        temp_list = [x["name"] for x in self.datas["send_to_list"]]
        temp_list.append("New entry")
        
        self.list_items.set(temp_list)
        print("Settings refreshed")
        
    def save_settings(self):
        # New entry
        if self.current_send_to.get() == "New entry":
            if not self.name_variable.get()\
            or not self.address_variable.get()\
            or not self.passphrase_variable.get()\
            or not self.port_variable.get():
                tk.messagebox.showerror("Error", "Invalid Entry")
                print("Invalid selection, avoiding save")
                return
                
            new_entry = {}
            new_entry["name"] = self.name_variable.get()
            new_entry["address"] = self.address_variable.get()
            new_entry["port"] = self.port_variable.get()
            new_entry["passphrase"] = self.passphrase_variable.get()
            new_entry["active"] = 1
            new_entry["clipboard_type"] = self.clipboard_variable.get()
            self.datas["send_to_list"].append(new_entry)
            print("Entry created")
            
        # Modify existing
        elif self.current_send_to.get() != "None":
            if not self.name_variable.get()\
            or not self.address_variable.get()\
            or not self.passphrase_variable.get()\
            or not self.port_variable.get():
                tk.messagebox.showerror("Error", "Invalid Entry")
                print("Invalid selection, avoiding save")
                return
            
            selected = self.datas["send_to_list"][self.current_index]
            
            selected["name"] = self.name_variable.get()
            selected["address"] = self.address_variable.get()
            selected["port"] = self.port_variable.get()
            selected["passphrase"] = self.passphrase_variable.get()
            selected["clipboard_type"] = self.clipboard_variable.get()
            print("Entry modified")
        
        # Invalid entry
        else:
            tk.messagebox.showerror("Error", "Invalid Entry")
            print("Invalid selection, avoiding save")
            return
        
        # Set new entry name
        self.current_send_to.set(self.name_variable.get())
        
        # Save json
        save_json(get_zouip_config_file(), self.datas)
        
        # Refresh settings
        self.refresh_settings()
            
        print("Settings saved")
        
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Set variables
        self.current_send_to = tk.StringVar()
        self.current_send_to.set("None")
        self.current_index = -1
        self.name_variable = tk.StringVar()
        self.address_variable = tk.StringVar()
        self.port_variable = tk.IntVar()
        self.passphrase_variable = tk.StringVar()
        self.clipboard_variable = tk.StringVar()
        self.list_items = tk.Variable()
        
        self.refresh_settings()

        # Set geometry
        parent.geometry("500x450")
        parent.resizable(True, True)
        parent.title("Zouip Send to Settings")

        ### Theming
        # Set padding
        parent['padx'] = 20
        parent['pady'] = 20
        # parent.grid_rowconfigure(0, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        row = 0
        
        # Config folder informations
        config_folder_label = tk.Label(
            parent,
            text="Config folder : /home/username/.config/zouip/",
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        # Refresh Settings
        refresh_settings_button = tk.Button(
            parent,
            text="Refresh Settings",
            command=self.refresh_settings,
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        ### Send to list_items
        
        self.send_to_list = tk.Listbox(
            parent,
            listvariable=self.list_items,
            height=5,
        )
        self.send_to_list.grid(row=row, column=0, sticky="we",columnspan=3)
        self.send_to_list.bind("<<ListboxSelect>>", self.get_selected_send_to)
        row += 1
        
        ### Settings
        
        # Current selection
        tk.Label(
            parent,
            text = "Selected : ",
        ).grid(row=row, column=0, sticky="w")
        tk.Label(
            parent,
            textvariable = self.current_send_to,
        ).grid(row=row, column=1, sticky="w")
        row += 1
        
        # Name
        name_label = tk.Label(
            parent,
            text = "Name",
        ).grid(row=row, column=0, sticky="w")
        name_entry = tk.Entry(
            parent,
            textvariable = self.name_variable,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Address
        address_label = tk.Label(
            parent,
            text = "Address",
        ).grid(row=row, column=0, sticky="w")
        address_entry = tk.Entry(
            parent,
            textvariable = self.address_variable,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Port
        port_label = tk.Label(
            parent,
            text = "Port",
        ).grid(row=row, column=0, sticky="w")
        port_entry = tk.Entry(
            parent,
            textvariable = self.port_variable,
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Passphrase
        passphrase_label = tk.Label(
            parent,
            text = "Passphrase",
        ).grid(row=row, column=0, sticky="w")
        passphrase_entry = tk.Entry(
            parent,
            textvariable = self.passphrase_variable,
            show="*",
        ).grid(row=row, column=1, sticky="we",columnspan=2)
        row += 1
        
        # Clipboard type
        clipboard_button0 = tk.Radiobutton(
            parent,
            text="Text and Files",
            variable=self.clipboard_variable,
            value="both",
        ).grid(row=row, column=0, sticky="w")
        clipboard_button1 = tk.Radiobutton(
            parent,
            text="Text",
            variable=self.clipboard_variable,
            value="text",
        ).grid(row=row, column=1, sticky="w")
        clipboard_button2 = tk.Radiobutton(
            parent,
            text="Files",
            variable=self.clipboard_variable,
            value="file",
        ).grid(row=row, column=2, sticky="w")
        row += 1
        
        ### Save
        save_settings_button = tk.Button(
            parent,
            text="Save Entry Settings",
            command=self.save_settings,
        ).grid(row=row, column=0, sticky="we", columnspan=3)
        row += 1
        
        ### Remove entry
        remove_entry_button = tk.Button(
            parent,
            text="Remove entry",
            command=self.remove_entry,
        ).grid(row=row, column=0, sticky="we", columnspan=3)


if __name__ == "__main__":
    root = tk.Tk()
    Zouip_main_window(root)
    # Zouip_main_settings_parent(root)
    # Zouip_receive_from_settings_parent(root)
    # Zouip_send_to_settings_parent(root)
    root.mainloop()
