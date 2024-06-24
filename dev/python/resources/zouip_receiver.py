import socket
import time
import os
import json
import subprocess


# TODO Empty receive folder if needed (config ?)
# TODO Timeout if not receiving after 1s


### Get common path
current_folder = os.path.dirname(os.path.realpath(__file__))
config_filepath = os.path.join(current_folder, "zouip_config.json")


def get_config_datas():
    if not os.path.isfile(config_filepath):
        return None
    with open(config_filepath, "r") as read_file:
        dataset = json.load(read_file)
    return dataset


def get_folder_size(folderpath):
    folder_size = 0
    for root, dirs, files in os.walk(folderpath):
        for f in files:
            folder_size += os.path.getsize(os.path.join(root, f))
    return folder_size


def get_file_list_from_request(request):
    
    file_list = request.split("]")
    
    for f in file_list:
        index = file_list.index(f)
        if f == "":
            file_list.pop(index)
            continue
        
        f = f.split("[")[1]
        # f = (f.split(";;")[0], f.split(";;")[1], f.split(";;")[2])
        f = f.split(";;")
        
        file_list[index] = f
        
    return file_list


##### INIT #####

### Get configuration
print("Reading configuration file")
config_datas = get_config_datas()

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
):
    
    # Get socket
    s = socket.socket()
    # Set socket reuse (to prevent timeout if closed before)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    
    while True:
        
        s.listen(5)
        c, addr = s.accept()
        
        print()
        print(f"Request from : {addr}")

        while True:
            
            # Get request from sender
            sender_request = c.recv(8192).decode()
            print(f"Request : {sender_request}")
            
            # Close command
            if sender_request == "close":
                print("Close request, quitting")
                c.close()
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                exit()
            
            # Check if valid receiver
            valid_sender = None
            for sender in get_config_datas()["receive_from_list"]:
                if addr[0] == sender["address"] and sender["active"]:
                    valid_sender = sender
                    break
                    
            if not valid_sender:
                print("Sender denied")
                c.send("Denied".encode())
                c.close()
                break

            ### Deny request if wrong passphrase or request form
            passphrase = get_config_datas()["passphrase"]
            if not sender_request.startswith(f"{passphrase};;")\
            or sender_request.split(";;")[1] not in {"files", "command"}:
                print("Request denied")
                c.send("Denied".encode())
                c.close()
                break
            
            ### File request
            elif sender_request.split(";;")[1] == "files":
            
                c.send("Granted".encode())
                print("Files download request granted")
                
                # Get files list
                file_list = get_file_list_from_request(sender_request)                
                file_number = len(file_list)
                
                c.close()
                
                # File receive
                print(f"Requesting {file_number} File(s)")
                
                for f in file_list:
                    
                    # Get remaining files number
                    remaining = len(file_list)-(file_list.index(f)+1)
                    
                    # Get file name
                    file_name = os.path.basename(f[0])
                    subdir = f[1]
                    
                    # Connect to client
                    s.listen(5)
                    c, addr = s.accept()
                    
                    # Check for clipboard type
                    if (file_name == "clipboard_content.txt"\
                    and valid_sender["clipboard_type"] == "file")\
                    or (file_name != "clipboard_content.txt"\
                    and valid_sender["clipboard_type"] == "text"):
                        print(f"Invalid clipboard type, avoiding")
                        request_file_message = f"avoid;;remaining:{remaining};;file:{f[0]}"
                        c.send(request_file_message.encode())
                        c.close()
                        continue
                    
                    # Check size (0=no limit)
                    size_limit = get_config_datas()["size_limit"]
                    if size_limit != 0:
                        if int(f[2]) > size_limit or int(f[3]) > size_limit:
                            print(f"File size exceeding size limit : {file_name}, avoiding")
                            request_file_message = f"avoid;;remaining:{remaining};;file:{f[0]}"
                            c.send(request_file_message.encode())
                            c.close()
                            continue
                    
                    # Get destination filepath
                    if file_name=="clipboard_content.txt":
                        file_name = "clipboard_from.txt"
                        
                    subroot_path = None
                    
                    # Get filepath with subdir
                    zouip_folder = get_config_datas()["zouip_folder"]
                    
                    if subdir!=".":
                        # Get filepath with subdir
                        filepath = os.path.join(
                            os.path.join(zouip_folder, subdir),
                            file_name
                        )
                    # Get filepath no subdir
                    else:
                        filepath = os.path.join(zouip_folder, file_name)
                    
                    # Check if file available in local folder
                    if (
                        os.path.isfile(filepath) and\
                        os.path.getsize(filepath) == int(f[2])
                    ):
                        print(f"File already available on disk : {file_name}, avoiding")
                        request_file_message = f"avoid;;remaining:{remaining};;file:{f[0]}"
                        c.send(request_file_message.encode())
                        c.close()
                        continue
                    
                    # Create subdir if needed
                    basedir = os.path.dirname(filepath)
                    os.makedirs(basedir, exist_ok=True)
                    
                    # Send file request from original request message
                    request_file_message = f"remaining:{remaining};;file:{f[0]}"
                    print(f"Requesting : {f[0]} - {f[2]}k")
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
            
            ### Command request
            elif sender_request.split(";;")[1] == "command":
                
                # Get command
                command = sender_request.split(";;")[2]
                
                # Execute it
                print(f"Executing command : {command}")
                subprocess.call(command, shell = True)
                
                c.send("Executed".encode())
                c.close()

            # sender_request = c.recv(1024).decode()
            # print(f"INPUT: {sender_request}")
            
            print(f"Closing connection with {addr}")
            
            c.close()

            break


print("Starting zouip receiver")
_socket_server(
    config_datas["receive_port"],
)
