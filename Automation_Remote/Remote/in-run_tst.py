import sys
import subprocess
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
# from datetime import datetime, timedelta, timezone
from datetime import datetime
import json

#========================================================================================================================================
# CONFIG:
# squishserver --config addAUT <build_name> "absolute_file_path"
# Ex: squishserver --config addAUT NocStudio_GUI-2557 "C:\\TanMai\\NocStudio\\NocStudio_GUI-2557.exe"
#========================================================================================================================================
#========================================================================================================================================
# CMD: 
# squishrunner --debugLog alpw --port 4322 --testsuite "absolute_folder_path" --aut <build_name> --reportgen text,"absolute_file_path"
# squishrunner --debugLog alpw --port 4322 --testsuite "absolute_folder_path" --aut <build_name> --reportgen html,"absolute_folder_path"
#========================================================================================================================================

testsuite_directory = []
sender_on_windows = 'ns_gui_regression@intel.com'

recipient=""

os.environ["DISPLAY"] = ":1.0"
platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()
# thisdir = os.getcwd()

def run_test(build_version=""):
    print "------------------------------------------------------------------------------"
    print "***Data details:"
    print "- ticket-id:{}".format(ticket)
    print "- build-version-name:{}".format(buildName)
    print "- test-suites:{}".format(listTestSuites)
    print "- schedule:{}".format(schedule)
    print "- listReports:{}".format(listReports)
    print "------------------------------------------------------------------------------"

    for mail in listReports:
        print "\t+ send_mail(to_addr={}, cc_mail=cc_mail0, subject=subject, content=content, file_location="")".format(mail)

#---------------------------------Define path folder of script-------------------------------------------
    report_directory = "C:\\TanMai\\squish_test_suite\\squish_test_suites_bdd\\html_report"
    base_test_directory = "C:\\TanMai\\squish_test_suite\\squish_test_suites_bdd\\"
    if "\\" in base_test_directory:
        base_test_directory = string.replace(base_test_directory, "\\", "/")
    print "------------------------------------------------------------------------------"
    print "***Folder all test suites: {}".format(base_test_directory)
    print "***Folder html report: {}".format(report_directory)
    print "------------------------------------------------------------------------------"
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
            print "***Selected folders:"
            for fol in folders:
                if fol in listTestSuites:
                    listTestSelected.append(fol)
                    print "\t+ {}".format(fol)
            print "------------------------------------------------------------------------------"
        print "***Valid folders:"
        for test in listTestSelected:
            testPath = os.path.join(base_test_directory, test, "{}.txt".format(sys.argv[i]))
            if os.path.exists(testPath):
                testsuite = base_test_directory + test
                if "\\" in testsuite:
                    testsuite = string.replace(testsuite, "\\", "/")
                testsuite_directory.append(testsuite)
                print "\t+ {}: {}".format(test, testsuite)
        print "------------------------------------------------------------------------------"
        print "***Size of list test suites: {}".format(str(len(testsuite_directory)))
        print "------------------------------------------------------------------------------"

    if len(testsuite_directory) == 0:
        return 
    
    # return

    start_squish_server()
    # config_squish_server(buildName)
    testsuite_directory.sort()
    start_time = time.time()
    
    if os.path.exists(report_directory):
        shutil.rmtree(report_directory)
    os.mkdir(report_directory)

    for d in (testsuite_directory):
        source_file ="C:\\Users\\maitanx\\backup_ini\\NocStudio.ini"
        destination_folder ="C:\\Users\\maitanx\\.NetSpeed\\"
        shutil.copy2(source_file, destination_folder)
        print "------------------------------------------------------------------------------"
        print "***In folder: " + d
        print "------------------------------------------------------------------------------"
        total_tsuite += 1
        # bash_command = "squishrunner --debugLog alpw --port 4322 --testsuite " + d + " --aut {} --reportgen html,{}".format(buildName, report_directory, report_directory + "\\results.txt")
        bash_command = "squishrunner --debugLog alpw --port 4322 --testsuite " + d + " --reportgen html,{} --reportgen stdout,{}".format(report_directory, report_directory + "\\report_{}.txt".format(d.split("/")[-1]))
        print "Begin execute testsuite"
        if os_system == platforms["Linux"]:
            process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
            print "Processing data..."
        else:            
            process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
            print "Processing data..."
        process.communicate()[0]
        time.sleep(3)
          
    temp = (time.time() - start_time) / 3600
    elapsed_time = float("{0:.2f}".format(temp))

    # time = schedule[0].split(":")
    # hour = int(time[0])
    # minute = int(time[1])
    # second = int(time[2])

    # date = schedule[1].split("/")
    # day = int(date[0])
    # month = int(date[1])
    # year = int(date[2])

    # serverTime = datetime(year, month, day, hour, minute, second)

    # localTimeZone = timezone(timedelta(hours=7))   # Local GMT+7
    # serverTimeZone = timezone(timedelta(hours=-7)) # Server GMT-7

    # serverTime = serverTime.replace(tzinfo=serverTimeZone)
    # localTime = serverTime.astimezone(localTimeZone)

    # timeValue = localTime.strftime("%H_%M_%S")
    # dateValue = localTime.strftime("%d_%m_%Y")

    total_tscase = getTotalTestcase()
    tscase_errors = getTestcaseErrors(report_directory)

    report_link = "\\\\samba.zsc11.intel.com\\nfs\\site\\proj\\CFG\\scratch2\\tanmaix\\tcp_auto\\report_[" + str(dateCurrently) + "]_[" + str(timeCurrently) + "]\\"
    os.system("xcopy " + report_directory + " " + report_link  + " /E/H/C/I/Y")

    subject = "GUI Automation Test Report for " + str(build_version)
    content = ""
    content += "This is the automation test report for NocStudio (Date: " + str(dateCurrently) + " - Time: " + str(timeCurrently) + "). \n"
    content +="\n";
    content += "- Total Test cases: " + str(total_tscase) + "\n"
    content += "- Total Time: " + str(elapsed_time) + "(h)\n"
    content += "- Failed Test cases: " + str(len(tscase_errors)) + "\n"
    content += "- Build Version Test: NocStudio_" + str(build_version) + "\n"
    content +="\n";
    content += "file:///" + report_link + "index.html" + "\n"

    results_file_path = [os.path.join(report_link, name) for name in os.listdir(report_link) 
                if os.path.isfile(os.path.join(report_link, name)) and name.endswith('.txt')]
    # results_file_path = report_link + "results.txt"
    
    for mail in listReports:
        send_mail(to_addr=mail, cc_mail="", subject=subject, content=content, file_location=results_file_path)

    shutil.rmtree(report_directory)

    stop_squish_server()

def config_squish_server(name):
    build_directory = "C:\\TanMai\\NocStudio\\{}".format(name)
    bash_command = "squishserver --config addAUT {} {}".format(name.split(".")[0], build_directory)
    if os_system == platforms["Linux"]:
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
    
    return process.returncode

def start_squish_server():
    bash_command = "squishserver --port 4322"
    if os_system == platforms["Linux"]:    
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
    
    return process.returncode

def stop_squish_server():
    bash_command = "squishserver --stop"
    if os_system == platforms["Linux"]:
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
    
    return process.returncode

def send_mail(to_addr="", cc_mail="", subject="Netspeed", content="Auto", file_location=[]):
    if os_system == platforms["Linux"]:
        bash_command = ["mail", "-s", subject, recipient]
        try:
            process = subprocess.Popen(bash_command, stdin=subprocess.PIPE)
        except Exception, error:
            print error
        process.communicate(content)
    else:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_on_windows
        msg['To'] = to_addr
        msg['CC'] = cc_mail
        recipient = to_addr.split(",") + cc_mail.split(",")
        
        msg.attach(MIMEText(content, 'plain'))

        # if file_location != "":
        #     filename = os.path.basename(file_location)
        #     attachment = open(file_location, "rb")
        #     part = MIMEBase('application', 'octet-stream')
        #     part.set_payload((attachment).read())
        #     encoders.encode_base64(part)
        #     part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        #     msg.attach(part)
        
        for file in file_location:
            filename = os.path.basename(file)
            attachment = open(file, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(part)
        
        s = smtplib.SMTP('smtp.intel.com')
        s.sendmail(sender_on_windows, recipient, msg.as_string())
        s.quit()
    print "Sent mail sucessfully!"

def getTotalTestcase():
    total_tst = 0
    for d in (testsuite_directory):
        for test in os.listdir(d):
            if test.startswith("tst_"):
                total_tst += 1
    return total_tst

def getTestcaseErrors(report_path):
    tstcase_errors = []
    data = []
    f = open(report_path + "\\data\\results-v1.js", "r")
    content = f.read().strip('\n')
    content = content.lstrip("var data = [];\ndata.push( ").rstrip(");")
    content_json = content.replace("data.push(", "").replace(");", ",\n");
    data = json.loads("[" + content_json + "]")

    for suites in data:
        for suite_data in suites["tests"]:
            for tst_data in suite_data["tests"]:
                if tst_data["type"] == "testcase":
                    tst_data_str = str(tst_data)
                    if "u'result': u'ERROR'" in tst_data_str or "u'result': u'FAIL'" in tst_data_str or "u'result': u'FATAL'" in tst_data_str:
                        tstcase_errors.append(tst_data["name"])
    f.close
    return tstcase_errors

if __name__ == "__main__":
    timeCurrently = datetime.now().strftime("%H_%M_%S")
    dateCurrently = datetime.today().strftime("%d_%m_%Y")
    print "[Currently: {} - {}] Running in-run_tst.py...".format(timeCurrently, dateCurrently)
    time.sleep(5)
    jsonFile = 'C:\\TanMai\\TuanNguyen\\input_{}.json'.format(sys.argv[1])
    with open(jsonFile, 'r') as f:
        data = json.load(f)
    print "***Data JSON:"
    print "{}".format(json.dumps(data, indent=2))
    ticket = data["ticket-id"]
    buildName = data["build-version-name"]
    listTestSuites = data["test-suites"]
    schedule = data["schedule"]
    timeValue = data["schedule"][0]
    dateValue = data["schedule"][1]
    listReports = data["reports"]
    run_test(ticket)
    time.sleep(5)
    os.system('del /f /q "C:\\TanMai\\TuanNguyen\\input_{}.json"'.format(sys.argv[1]))
    print "Finished."
    print "Run automation successful."
    time.sleep(3)