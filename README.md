# uPyFile
This is a file management tool for use with MicroPython (uPython). It works by sending Ctrl+C to the device in order to stop execution of whatever script may be running, then waits for a REPL prompt. It then sends the python commands to open the correct file and read/write it.

Currently, the program is pretty functional. It has a working installer (just download or clone this project and run the installer) and currently supports the following operations:

* Reading files
* Pushing files from the PC to the device
* Pulling files from the device to the PC
* Listing directory contents

## Compiling:
Compiling requires the Python packages `nuitka` and `pySerial`. The folders `uPyFile.build` and `uPyFile.dist` will be created (or `install.build` and `install.dist` if compiling the installer). They can safely be ignored or deleted. Compiling the installer is not necessary unless it has been modified.

### Linux:
```shell
python3 -m nuitka uPyFile.py --onefile -o uPyFile
python3 -m nuitka install.py --onefile -o install
```

### Windows:
```
python3 -m nuitka uPyFile.py --onefile -o uPyFile.exe
python3 -m nuitka install.py --onefile -o install.exe
```

## Installing:
Clone the repository or click the green `Code` button and open a terminal in the downloaded folder.

### Linux:
Run:
```
$ sudo ./install
$ sudo chmod 775 /usr/local/bin/uPyFile/*
$ sudo ln -s /usr/local/bin/uPyFile/uPyFile /usr/local/bin/upyfile
```

### Windows:
Run `./install` and add `C:\Users\%USERNAME%\AppData\Local\Programs\uPyFile` to PATH.
