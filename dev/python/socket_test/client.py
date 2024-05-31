import socket, os

file_list = [
    r"/home/tonton/Pictures/etoilephospho02_nuit.jpg",
    r"/home/tonton/Téléchargements/log.html",
]
    

def _socket_send(
    host,
    port,
    request,
    file_list,
):
    
    # Connect to server
    s = socket.socket()
    try:
        s.connect((host,port))
    except ConnectionRefusedError:
        print(f"Unable to connect to {host}-{port}, aborting")
        return False
    
    # Send server request
    print(f"Sending request to {host}-{port} - {request}")
    s.send(request.encode())
    
    # Get server answer
    answer = s.recv(1024).decode()
    
    # Check if answer positive
    if answer=="Denied":
        print(f"Request denied by {host}-{port}, aborting")
        s.close()
        return False
    print(f"Request granted by {host}-{port}, sending content")
    s.close()
    
    # Send files
    for filepath in file_list:
        # Connect
        s = socket.socket()
        s.connect((host,port))
        
        # Send info message
        print(f"Sending {filepath} to {host}-{port}")
        file_message = f"{os.path.basename(filepath)};;0"
        s.send(file_message.encode())
        
        # Send file
        f = open(filepath, "rb", encoding=None)
        s.sendfile(f)
        
        s.close()
    
    # Close connection
    print(f"Closing connection with {host}-{port}")
    
    return True

    
_socket_send("0.0.0.0", 22344, "azerty;;2", file_list)
