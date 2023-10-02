# uPyFile

This is a file management tool for use with MicroPython (uPython).

## Quick how-to

* Initialize a device with `$ upyfile -p /dev/ttyACM0 init`
* Read the contents of a file on a device in the terminal with `$ upyfile -p /dev/ttyACM0 read /file/on/dev`
* Push a file to a device with `$ upyfile -p /dev/ttyACM0 push /file/on/pc /file/on/dev`
* Pull a file from a device with `$ upyfile -p /dev/ttyACM0 pull /file/on/dev /file/on/pc`
* List files on a device with `$ upyfile -p /dev/ttyACM0 list /dir/to/list`

Windows users should use DOS paths (`path\to\file`) when referencing a file on the PC, but should still use UNIX paths (`path/to/file`) when referencing a file or directory on a device.

If the device does not seem to be communicating properly, check its documentation to be sure that you aren't overrunning its UART buffer and set the appropriate buffer size with the `-B` argument.

## Building

Compiling requires the Python packages `nuitka` and `pySerial`. Use the command `python3 -m nuitka upyfile.py --standalone --include-data-file=stub.py=stub.py`. The folders `uPyFile.build` and `uPyFile.dist` will be created. They can safely be ignored or deleted.

### Linux

```shell
python3 -m nuitka upyfile.py --standalone --include-data-file=stub.py=stub.py
```

### Windows

```shell
python -m nuitka upyfile.py --standalone --include-data-file=stub.py=stub.py
```

## Installing

Fetch the desired release from https://github.com/AwesomeCronk/uPyFile/releases

### Linux

* Unpack it to `/usr/local/bin/`
* `$ cd /usr/local/bin && sudo ln -s /usr/local/bin/upyfile-<version.goes.here>-linux/upyfile upyfile`

### Windows

* Unpack it or `%LOCALAPPDATA%\Programs\`
* Add `%LOCALAPPDATA%\Programs\uPyFile-<version-goes-here>-Windows` to your user path
