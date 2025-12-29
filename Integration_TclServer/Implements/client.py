import sys
import socket

#SERVER_IP = "127.0.0.1"            #Default - Accept all client IP address
#SERVER_IP = "10.21.0.218"          #Local - Only accept local IP address
#SERVER_IP = "10.116.181.184"       #ION - Virtual Machine (The IP address of session running server)
#SERVER_PORT = 10001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(5)

try:
    while True:
        SERVER_IP = input(">>> IP: ").strip()
        if not SERVER_IP:
            continue
        SERVER_PORT = int(input(">>> Port: ").strip())
        if not SERVER_PORT:
            continue
        break
except KeyboardInterrupt:
    sys.exit(0)

try:
    client.connect((SERVER_IP, SERVER_PORT))
    print(f">>> [Connection information]: Connected to {SERVER_IP}:{SERVER_PORT}\n")
except socket.timeout:
    print(">>> Connection failed.")
    client.close()
    sys.exit(0)
except (ConnectionRefusedError, OSError):
    print(">>> Connection failed.")
    client.close()
    sys.exit(0)

init = False
waiting = False

try:
    while True:
        try:
            if not init:
                msg = ">>> Connection is established successfully."
            elif not waiting:
                msg = input("$ ").strip()
                waiting = True

            if not msg:
                waiting = False
                continue

            if msg.lower() in ("exit", "quit"):
                print(">>> Connection have been closed by client.")
                break

            # Send request
            client.sendall((msg + "\n").encode())
            if not init:
                init = True
                continue
            
            # Clear message
            msg = ""

            # Waiting for response
            while waiting:
                data = client.recv(1024)
                if not data:
                    print(">>> Application has been closed. Connection have been closed by server.")
                    sys.exit(0)
                text = data.decode('utf-8')
                lines = text.splitlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        if line == "Complete":
                            waiting = False
                            break
                        print(f"{line}")
            print()
        except KeyboardInterrupt:
            print(">>> Connection have been closed by client")
            break
except KeyboardInterrupt:
    print(">>> Connection have been closed by client")