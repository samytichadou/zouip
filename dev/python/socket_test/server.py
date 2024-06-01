import socket, time, os

passphrase = "azerty"
receive_folder = "/home/tonton/Téléchargements/zouip/receive_server/"

def _socket_server(
    port,
    passphrase,
    receive_folder,
):  
    
    s = socket.socket()
    s.bind(('', port))
    
    while True:
        s.listen(5)
        c, addr = s.accept()
        print(f"Request from : {addr}")

        while True:
            rcvdData = c.recv(1024).decode()
            
            # Deny request if wrong passphrase
            if not rcvdData.startswith(f"{passphrase};;"):
                print("Request denied")
                c.send("Denied".encode())
                c.close()
                break
            
            file_number = int(rcvdData.split(";;")[1])
            
            print("Request granted")
            c.send("Granted".encode())
            
            # File receive
            print(f"Receiving {file_number} Files")
            
            c.close()
            
            for i in range(file_number):
                # Connect
                s.listen(5)
                c, addr = s.accept()
                
                # Get file info
                file_message = c.recv(1024).decode()
                name, size = file_message.split(";;")
                
                # Get filepath
                if name=="clipboard_content.txt":
                    name = "clipboard_from.txt"
                filepath = os.path.join(receive_folder, name)
                                        
                # # Remove file if existing
                # if os.path.isfile(filepath):
                #     os.remove(filepath)

                # Receive file
                print(f"Receiving : {name}")
                filetodown = open(filepath, "wb")
                data = c.recv(1024)
                while data:
                    filetodown.write(data)
                    data = c.recv(1024)
                print(f"Received : {name}")
                filetodown.close()
                
                # Close connection
                c.close()
            
            # rcvdData = c.recv(1024).decode()
            # print(f"INPUT: {rcvdData}")
            
            print(f"Closing connection with {addr}")

            break

_socket_server(12345, passphrase, receive_folder)
