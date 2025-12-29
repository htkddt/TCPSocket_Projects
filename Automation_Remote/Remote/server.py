import os
import socket
import subprocess
import platform
import json

platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()

jsonDir = "C:\\TanMai\\TuanNguyen\\"
buildDir = "C:\\TanMai\\NocStudio\\"
testDir = "C:\\TanMai\\squish_test_suite\\squish_test_suites_bdd\\"

HOST = '0.0.0.0'
PORT = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
print "Server listenning on [{}:{}]...".format(HOST, PORT)
while True:
    conn, addr = s.accept()
    print "Connected from {}".format(addr)
    print "------------------------------------------------------------------------------"
    connected = True
    while True:
        recvJSON = ""
        while not recvJSON.endswith("\n"):
            recvJSON += conn.recv(1).decode()
        if recvJSON:
            try:
                recvData = json.loads(recvJSON.strip())
            except json.JSONDecodeError, e:
                print "{}".format(e)
            if len(recvData) == 2:
                if recvData["argv"] == "server":
                    if recvData["value"] == "init":
                        print "Request to collect available data from client"
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
                        print "Collect available data successful"
                        print "------------------------------------------------------------------------------"
                        continue
                    elif recvData["value"] == "close" or recvData["value"] == "stop":
                        sendData = {
                            "argv":"client",
                            "value":"disconnected"
                        }
                        sendJSON = json.dumps(sendData)
                        conn.sendall((sendJSON + "\n").encode())
                        if recvData["value"] == "close":
                            print "Server was disconnected by user"
                            connected = False
                            break
                        if recvData["value"] == "stop":
                            print "Server listenning on [{}:{}]...".format(HOST, PORT)
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
                        print "Request to add new build file from client"
                        fileName = recvData["value"][0] + ".exe"
                        fileSize = int(recvData["value"][1])
                        destPath = os.path.join(buildDir, fileName)
                        # print "destPath: {}".format(destPath)
                        # print "fileName: {}".format(fileName)
                        # print "fileSize: {}".format(str(fileSize))
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
                        print "Save build successful"
                        print "------------------------------------------------------------------------------"
                else:
                    sendData = {
                        "argv":"client",
                        "value":"error"
                    }
                    sendJSON = json.dumps(sendData)
                    conn.sendall((sendJSON + "\n").encode())
                    print "ERROR: Incorrect request from client\nTo disconnect type: server stop or client stop"
                    print "------------------------------------------------------------------------------"
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
                isExistingTask = os.system('schtasks /query /tn "Task_{}" >nul 2>&1'.format(ticket))
                if isExistingTask == 0: os.system('schtasks /delete /tn "Task_{}" /f'.format(ticket))
                cmdPARA = {
                    "ticket-id":ticket,
                    "build-version-name":buildName,
                    "test-suites":testSuites,
                    "schedule":schedule,
                    "reports":reports
                }
                jsonFile = os.path.join(jsonDir, "input_{}.json".format(ticket))
                with open(jsonFile, 'w') as f:
                    json.dump(cmdPARA, f)
                # cmdJSON = json.dumps(cmdPARA)
                # cmd = "python2 in-run_tst.py " + ticket + " bdd_test"
                cmd = "schtasks /create /tn \"Task_{}\" /tr \"C:\\TanMai\\TuanNguyen\\run.bat {}\" /sc once /st {} /sd {}".format(ticket, ticket, timeValue, dateValue)
                sendData = {
                    "argv":"status",
                    "value":"running"
                }
                sendJSON = json.dumps(sendData)
                conn.sendall((sendJSON + "\n").encode())
                try:
                    if os_system == platforms["Linux"]:    
                        # process = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        process = subprocess.call(cmd)
                    else:
                        # process = subprocess.Popen(cmd.split(), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        process = subprocess.call(cmd, shell=True)
                    # process.communicate(input=cmdJSON.encode())
                except Exception, error:
                    print "Error: " + str(error)
                if conn:
                    sendData = {
                        "argv":"status",
                        "value":"finished"
                    }
                    sendJSON = json.dumps(sendData)
                    conn.sendall((sendJSON + "\n").encode())
                print "------------------------------------------------------------------------------"
    if not connected: break