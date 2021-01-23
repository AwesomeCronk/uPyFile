This is a file management tool for use with MicroPython (uPython). It works by sending Ctrl+C to the device in order to stop execution of whatever script may be running, then waits for a REPL prompt. It then sends the python commands to open the correct file and read/write it.

Usage:

python uPyFile.py port read deviceFileName  -  reads a file from the device and prints its contents to the terminal.

python uPyFile.py port pull deviceFileName pcFileName  -  copies a file from the device to your PC.

python uPyFile.py port push pcFileName deviceFileName  -  copies a file from your PC to the device.

Examples:

python uPyFile.py COM3 read boot.py

python uPyFile.py COM12 pull main.py

Currently, the program is pretty functional. It has a working installer (just download or clone this project and run the installer) and currently supports the following operations:

* Reading files
* Pushing files from the PC to the device
* Listing directory contents