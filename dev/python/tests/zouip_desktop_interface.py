from tkinter import *
from tkinter import filedialog

# Get config datas

root = Tk()

def get_folder(): 
    folder = filedialog.askdirectory(initialdir = "~/",title = "Select zouip folder")
    if folder is not None: 
        folderpath.set(folder)

folderpath = StringVar()
folderpath.set("/home/")

folderpath_label = Label(root, text="Zouip Folder : ")
folderpath_entry = Entry(root, textvariable=folderpath, width=30)
folderpath_button = Button(root, text="Browse", command=lambda:get_folder())

folderpath_label.grid(row=0, column=0)
folderpath_entry.grid(row=0, column=1)
folderpath_button.grid(row=0, column=2)
# zouipfolder_button.pack()

# receiver_frame = Frame(root, borderwidth=2, relief=GROOVE)
# receiver_frame.grid(row=1, column=0, fill="both", expand="yes")

Label(receiver_frame, text="Frame 1").pack(padx=10, pady=10)

root.mainloop()
