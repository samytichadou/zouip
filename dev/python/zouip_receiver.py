import socket
import time
import os
import json


# TODO Empty receive folder if needed (config ?)
# TODO Timeout if not receiving after 1s


### Get common path
current_folder = os.path.dirname(os.path.realpath(__file__))
config_filepath = os.path.join(current_folder, "zouip_config.json")

def read_json(filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset


##### INIT #####

### Get configuration
print("Reading configuration file")
config_datas = read_json(config_filepath)

if config_datas is None:
    print("No configuration file, aborting")
    exit()
    
print(config_datas)

### Create zouip dirs if needed
zouip_folder = config_datas["zouip_folder"]
if not os.path.isdir(zouip_folder):
    print(f"Creating zouip folder : {zouip_folder}")
    os.makedirs(zouip_folder)
else:
    print(f"Zouip folder found : {zouip_folder}")


def _socket_server(
    port,
    passphrase,
    receive_folder,
    size_limit
):
    
    # Get socket
    s = socket.socket()
    s.bind(('', port))
    
    while True:
        s.listen(5)
        c, addr = s.accept()
        print(f"Request from : {addr}")

        while True:
            # Get request from sender
            sender_request = c.recv(8192).decode()
            
            # Deny request if wrong passphrase
            if not sender_request.startswith(f"{passphrase};;"):
                print("Request denied")
                c.send("Denied".encode())
                c.close()
                break
            
            print("Request granted")
            c.send("Granted".encode())
            
            # Get files list
            file_list = sender_request.split("]")
            for f in file_list:
                index = file_list.index(f)
                if f == "":
                    file_list.pop(index)
                    continue
                f = f.split("[")[1]
                f = (f.split(";;")[0]), f.split(";;")[1]
                file_list[index] = f
                
            file_number = len(file_list)
            
            c.close()
            
            # File receive
            print(f"Requesting {file_number} File(s)")
            
            for f in file_list:
                
                # Get remaining files number
                remaining = len(file_list)-(file_list.index(f)+1)
                
                # Get file name
                file_name = os.path.basename(f[0])
                
                # Connect to client
                s.listen(5)
                c, addr = s.accept()
                
                # Check size
                if int(f[1]) > size_limit:
                    print(f"File size exceeding size limit : {file_name}, avoiding")
                    request_file_message = f"avoid;;remaining:{remaining};;file:{f[0]}"
                    c.send(request_file_message.encode())
                    c.close()
                    continue
                
                # Get destination filepath
                if file_name=="clipboard_content.txt":
                    file_name = "clipboard_from.txt"
                filepath = os.path.join(zouip_folder, file_name)
                
                # Check if file available in local folder
                if os.path.isfile(filepath)\
                and os.path.getsize(filepath) == int(f[1]):
                    print(f"File already available on disk : {file_name}, avoiding")
                    request_file_message = f"avoid;;remaining:{remaining};;file:{f[0]}"
                    c.send(request_file_message.encode())
                    c.close()
                    continue
                
                # Send file request from original request message
                request_file_message = f"remaining:{remaining};;file:{f[0]}"
                print(f"Requesting : {f[0]} - {f[1]}k")
                print(f"Remaining files to request : {remaining}")
                c.send(request_file_message.encode())
                
                # Wait for file incoming
                data = c.recv(1024) # TODO file not found error

                # Invalid file signal
                if len(data)==0:
                    print(f"Invalid file on remote : {f[0]}, avoiding")
                    c.close()
                    continue
                
                # Download file
                filetodown = open(filepath, "wb")
                request_file_message = f"Receiving file : {f[0]}"
                while data:
                    filetodown.write(data)
                    data = c.recv(1024)
                print(f"Received : {filepath}")
                filetodown.close()
                                        
                # Close connection
                c.close()
            
            # sender_request = c.recv(1024).decode()
            # print(f"INPUT: {sender_request}")
            
            print(f"Closing connection with {addr}")

            break


print("Starting zouip receiver")
_socket_server(
    config_datas["receiver"]["receive_port"],
    config_datas["receiver"]["passphrase"],
    config_datas["zouip_folder"],
    config_datas["receiver"]["size_limit"],
)
