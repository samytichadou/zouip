def send_sms(): 
    number_ = number.get()
    content_ = content.get()
    print(f"Sending sms to {number_}")
    return True

import tkinter as tk

root = tk.Tk()

label1 = tk.Label(root, text="Phone Number : ")
label1.pack()
number = tk.Entry(root)
number.pack()
label2 = tk.Label(root, text="Content : ")
label2.pack()
content = tk.Entry(root)
content.pack()
button = tk.Button(root, text="Send", command=send_sms)
button.pack()

root.mainloop()
