# coding=utf-8

import os
import subprocess
import sys
from json import loads

from src.utils.custom_path import Path

__version__ = None

if hasattr(sys, 'frozen'):
    __version__ = Path(sys.executable).get_win32_file_info().file_version
elif os.environ.get('APPVEYOR'):
    __version__ = loads(subprocess.check_output(
        [r'C:\ProgramData\chocolatey\bin\gitversion.exe']).decode().rstrip()).get('SemVer')
else:
    # This is a potential security breach, but I'm leaving it as is as it should only be running scripted
    # print(loads(subprocess.check_output(
    #     [r'C:\ProgramData\chocolatey\bin\gitversion.exe']).decode().rstrip()))
    __version__ = loads(subprocess.check_output(['gitversion']).decode().rstrip()).get('SemVer')

__guid__ = '4ae6dbb7-5b26-43c6-b797-2272f5a074f3'
