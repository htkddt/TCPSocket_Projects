import os
import socket
import subprocess
import platform
import json

platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()

jsonDir = f"C:\\Users\\tuanng4x\\Workspace\\Tickets\\TCP_AutomationTool\\Local"
buildDir = f"C:\\Users\\tuanng4x\\Workspace\\SVN"
testDir = f"C:\\Users\\tuanng4x\\Workspace\\Tickets\\Suite_nocstudio"

HOST = '127.0.0.1'
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Server listenning [{HOST}:{PORT}]...")
    while True:
        conn, addr = s.accept()
        print(f"Connected from {addr}")
        print("------------------------------------------")
        connected = True
        while True:
            recvJSON = ""
            while not recvJSON.endswith("\n"):
                recvJSON += conn.recv(1).decode()
            if recvJSON:
                try:
                    recvData = json.loads(recvJSON.strip())
                except json.JSONDecodeError as e:
                    print(e)
                if len(recvData) == 2:
                    if recvData["argv"] == "server":
                        if recvData["value"] == "init":
                            print("Collect available data for client")
                            files = [os.path.splitext(name)[0] for name in os.listdir(buildDir) 
                                       if os.path.isfile(os.path.join(buildDir, name)) and name.endswith('.exe')]
                            folders = [name for name in os.listdir(testDir) 
                                       if os.path.isdir(os.path.join(testDir, name)) and not name.startswith('.')]
                            sendData = {
                                "argv":"client",
                                "value": {
                                    "build-version":files,
                                    "test-suites":folders
                                }
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            print("------------------------------------------")
                            continue
                        elif recvData["value"] == "close" or recvData["value"] == "stop":
                            sendData = {
                                "argv":"client",
                                "value":"disconnected"
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            if recvData["value"] == "close":
                                print("Server was disconnected by user")
                                connected = False
                                break
                            if recvData["value"] == "stop":
                                print(f"Server listenning [{HOST}:{PORT}]...")
                                break
                        else:
                            sendData = {
                                "argv":"client",
                                "value":"error"
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            continue
                    elif recvData["argv"] == "header":
                        if recvData["value"] == "update":
                            filesUpdated = [os.path.splitext(name)[0] for name in os.listdir(buildDir) 
                                            if os.path.isfile(os.path.join(buildDir, name)) and name.endswith('.exe')]
                            sendData = {
                                "argv":"updated",
                                "value": filesUpdated
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                        else:
                            print("Request to add new build file from client")
                            fileName = recvData["value"][0] + ".exe"
                            fileSize = int(recvData["value"][1])
                            destPath = os.path.join(buildDir, fileName)
                            with open(destPath, 'wb') as f:
                                size = 0
                                while size < fileSize:
                                    bin = conn.recv(min(4096, fileSize - size))
                                    if not bin:
                                        break
                                    f.write(bin)
                                    size += len(bin)
                            sendData = {
                                "argv":"status",
                                "value":"successful"
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            print("------------------------------------------")
                    else:
                        sendData = {
                            "argv":"client",
                            "value":"error"
                        }
                        sendJSON = json.dumps(sendData)
                        conn.sendall((sendJSON + "\n").encode())
                        print("ERROR: Incorrect request from client\nTo disconnect type: server stop or client stop")
                        print("------------------------------------------")
                        continue
                else:
                    ticket = recvData["ticket-id"]
                    buildName = recvData["build-version-name"] + ".exe"
                    # buildSize = int(recvData["build-version-size"])
                    # if buildSize != 0:
                    #     destPath = os.path.join(buildDir, buildName)
                    #     with open(destPath, 'wb') as f:
                    #         size = 0
                    #         while size < buildSize:
                    #             bin = conn.recv(min(4096, buildSize - size))
                    #             if not bin:
                    #                 break
                    #             f.write(bin)
                    #             size += len(bin)
                    testSuites = recvData["test-suites"]
                    schedule = recvData["schedule"]
                    timeValue = schedule[0]
                    dateValue = schedule[1]
                    reports = recvData["reports"]
                    isExistingTask = os.system(f'schtasks /query /tn "Task_{ticket}" >nul 2>&1')
                    if isExistingTask == 0: os.system(f'schtasks /delete /tn "Task_{ticket}" /f')
                    cmdPARA = {
                        "ticket-id":ticket,
                        "build-version-name":buildName,
                        "test-suites":testSuites,
                        "schedule":schedule,
                        "reports":reports
                    }
                    jsonFile = os.path.join(jsonDir, f"input_{ticket}.json")
                    with open(jsonFile, 'w') as f:
                        json.dump(cmdPARA, f)
                    # cmdJSON = json.dumps(cmdPARA)
                    # cmd = f"python in-run_tst.py bdd_test"
                    cmd = f"schtasks /create /tn \"Task_{ticket}\" /tr \"C:\\Users\\tuanng4x\\Workspace\\Tickets\\TCP_AutomationTool\\Local\\run.bat {ticket}\" /sc once /st {timeValue} /sd {dateValue}"
                    sendData = {
                        "argv":"status",
                        "value":"running"
                    }
                    sendJSON = json.dumps(sendData)
                    conn.sendall((sendJSON + "\n").encode())
                    try:
                        if os_system == platforms["Linux"]:
                            # process = subprocess.run(cmd.split(), input=cmdJSON.encode())
                            process = subprocess.call(cmd)
                        else:
                            # process = subprocess.run(cmd, shell=True, input=cmdJSON.encode())
                            process = subprocess.call(cmd, shell=True)
                    except Exception as error:
                        print("Error: " + error)
                    if conn:
                        sendData = {
                            "argv":"status",
                            "value":"finished"
                        }
                        sendJSON = json.dumps(sendData)
                        conn.sendall((sendJSON + "\n").encode())
                    print("------------------------------------------")
        if not connected: break