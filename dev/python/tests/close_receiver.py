import os
import json
import socket


def get_zouip_config_file():
    home_folder = os.environ['HOME']
    config_folder = os.path.join(home_folder, ".config")
    zouip_folder =  os.path.join(config_folder, "zouip")
    return os.path.join(zouip_folder,"zouip_config.json")

def get_config_datas():
    config_filepath = get_zouip_config_file()
    
    if not os.path.isfile(config_filepath):
        return None
    with open(config_filepath, "r") as read_file:
        dataset = json.load(read_file)

    return dataset


def _socket_send_close(
    port,
):
    # Connect to server
    s = socket.socket()
    try:
        s.connect(("0.0.0.0",int(port)))
    except ConnectionRefusedError:
        print(f"Unable to connect to port {port}, aborting")
        return False
    
    # Close request
    request = f"close"
    
    # Send server request print(f"Sending request to {host}-{port} - {request}")
    print(f"Sending close request on port {port}")
    s.send(request.encode())
    
    # Close connection
    s.close()
    print(f"Closing receiver on port {port}")
    
    return True


### Get configuration
print("Reading configuration file")
config_datas = get_config_datas()

if config_datas is None:
    print("No configuration file, aborting")
    exit()

### Close receiver
_socket_send_close(
    config_datas["receive_port"]
)
