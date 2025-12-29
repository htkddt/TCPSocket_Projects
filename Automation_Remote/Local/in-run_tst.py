from glob import glob
import sys
import subprocess
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import shutil
import platform
import time
import string
# from string import replace
from datetime import datetime
import json

#====================================================
testsuite_directory = []
sender_on_windows = 'ns_gui_regression@intel.com'

recipient=""

os.environ["DISPLAY"] = ":1.0"
platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()
thisdir = os.getcwd()

def run_test(build_version=""):
    print("------------------------------------------")
    print("***Data details:")
    print(f"- ticket-id:{ticket}")
    print(f"- build-version-name:{buildName}")
    print(f"- test-suites:{listTestSuites}")
    print(f"- schedule:{schedule}")
    print(f"- listReports:{listReports}")
    print("------------------------------------------")
    for mail in listReports:
        print(f"\t+ send_mail(to_addr={mail}, cc_mail=cc_mail0, subject=subject, content=content, file_location="")")

#---------------------------------Define path folder of script-------------------------------------------
    base_test_directory = "C:/Users/tuanng4x/Workspace/Tickets/Suite_nocstudio"
    print("------------------------------------------")
    print(f"***Folder all test suites: {base_test_directory}")
    print("------------------------------------------")
#--------------------------------------------------------------------------------------------------------

    total_tsuite = 0
    total_tscase = 0
    tscase_errors = []
    
    args = sys.argv
    for i in range(2, len(args)):
        if os_system == platforms["Linux"]: return
        else:
            folders = [name for name in os.listdir(base_test_directory) 
                        if os.path.isdir(os.path.join(base_test_directory, name)) and not name.startswith('.')]
            listTestSelected = []
            print("***Selected folders:")
            for fol in folders:
                if fol in listTestSuites:
                    listTestSelected.append(fol)
                    print(f"\t+ {fol}")
            print("------------------------------------------")
        print("***Valid folders:")
        for test in listTestSelected:
            testPath = os.path.join(base_test_directory, test, f"{sys.argv[i]}.txt")
            if os.path.exists(testPath):
                testsuite = base_test_directory + "/" + test
                testsuite_directory.append(testsuite)
                print(f"\t+ {test}: {testsuite}")
        print("------------------------------------------")
        print(f"***Size of list test suites: {str(len(testsuite_directory))}")
        print("------------------------------------------")

if __name__ == "__main__":
    timeCurrently = datetime.now().strftime("%H:%M:%S")
    dateCurrently = datetime.today().strftime("%d/%m/%Y")
    print(f"[Currently: {timeCurrently} - {dateCurrently}] Running in-run_tst.py...")
    print("Processing in-run_tst.py with schtasks command...")
    time.sleep(5)
    jsonFile = f"C:\\Users\\tuanng4x\\Workspace\\Tickets\\TCP_AutomationTool\\Local\\input_{sys.argv[1]}.json"
    with open(jsonFile, 'r') as f:
        data = json.load(f)
    print("***Data JSON:")
    print(json.dumps(data, indent=2))
    ticket = data["ticket-id"]
    buildName = data["build-version-name"]
    listTestSuites = data["test-suites"]
    schedule = data["schedule"]
    timeValue = data["schedule"][0]
    dateValue = data["schedule"][1]
    listReports = data["reports"]
    run_test(ticket)
    time.sleep(5)
    print("Processing in-run_tst.py with schtasks command...")
    time.sleep(5)
    print("Processing in-run_tst.py with schtasks command...")
    time.sleep(5)
    print("Processing in-run_tst.py with schtasks command...")
    time.sleep(5)
    os.system(f'del /f /q "C:\\Users\\tuanng4x\\Workspace\\Tickets\\TCP_AutomationTool\\Local\\input_{sys.argv[1]}.json"')
    time.sleep(5)
    print("Finished.")
    print("Run automation successful.")
    time.sleep(3)