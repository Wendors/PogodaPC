# -*- coding: utf-8 -*-
__author__ = 'Сергі Полунець'
__versions__ = "v.3.7.2-86 - PySide6"
import os
import sys
import subprocess

names = "PogodaPC"
scripts = "PogodaPC"
icons = "PogodaPC"
num = 2

# Для Linux/Unix систем
if sys.platform.startswith('linux') or sys.platform == 'darwin':
    path_separator = ":"
    # Отримуємо шлях до PySide6
    try:
        result = subprocess.run([sys.executable, '-c', 'import PySide6; print(PySide6.__path__[0])'], 
                              capture_output=True, text=True)
        pyside6_path = result.stdout.strip()
    except:
        pyside6_path = ""
else:
    # Для Windows
    path_separator = ";"
    # Шлях для Windows (може потребувати коригування)
    path = '"C:/Program Files (x86)/Windows Kits/10/Redist/10.0.17763.0/ucrt/DLLs/x86"'
    try:
        result = subprocess.run([sys.executable, '-c', 'import PySide6; print(PySide6.__path__[0])'], 
                              capture_output=True, text=True)
        pyside6_path = result.stdout.strip()
    except:
        pyside6_path = 'C:/Python/Lib/site-packages/PySide6'

if str(num) == "1":
    pacs = "--onefile --console"
elif str(num) == "2":
    pacs = "--windowed"
elif str(num) == "3":
    pacs = "--onefile --windowed"
else:
    pacs = "--console"

# Команда для Linux/Unix
if sys.platform.startswith('linux') or sys.platform == 'darwin':
    icon_param = f"--icon={icons}.ico" if os.path.exists(f"{icons}.ico") else ""
    paths_param = f"--paths={pyside6_path}" if pyside6_path else ""
    cmd = f"pyinstaller {pacs} {icon_param} {scripts}.py --name={names} {paths_param} --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets"
else:
    # Команда для Windows
    cmd = f"pyinstaller.exe {pacs} --icon={icons}.ico {scripts}.py --name={names} --paths={path} --paths={pyside6_path} --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets"

print(f"Executing: {cmd}")
os.system(cmd)
#os.system("del /a " + "{0}.spec".format(names))
