import os
import shutil
import PyInstaller.__main__

# os.system('pyinstaller --onefile --noconsole --name TCPAutomation --icon=nsicon.ico --distpath=. ./App/applicationCore.py')
# try:
#     import PyInstaller.__main__
# except ImportError:
#     import subprocess
#     subprocess.check_call(['pip', 'install', 'pyinstaller'])
#     import PyInstaller.__main__

PyInstaller.__main__.run([
    '--onefile',
    '--noconsole',
    '--name=TCPAutomation',
    '--icon=nsicon.ico',
    '--distpath=.',
    './App/applicationCore.py'
])

if os.path.exists("build"):
    shutil.rmtree("build")