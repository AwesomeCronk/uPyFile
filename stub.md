The [stub program](/stub.py) is uploaded to the device when `init` is run. It runs commands to make things a touch easier on the PC end of things whithout increasing the overhead on the device too much.

A few notes:
* All hex data is presented in uppercase, no leading `0x`.
* All hex data is exchanged in batches of 1024 bytes, regardless of buffer size.
* The stub will print `ready~` when prompting for a command.
* The stub will print `~~recvd:` when a command is received.
* All commands will print `~~error:reason` on an error.
* All commands will print `~~complete:` when finished.

## Commands
* list <path>
  Prints the names of all files and folders in the specified directory, separated by newlines.

* ilist <path>
  Prints the names of all files and folders in the specified directory, including the type and size, separated by newlines.

* read <path>
  Opens the specified file and reads it's contents into the buffer. Clears existing buffer contents.

* write <path>
  Opens the specified file and writes the contents of the buffer into it.

* readbuf
  Prints out the first so many bytes of the buffer in uppercase hex, up to the configured batch size. Newline indicates end of data.

* writebuf <data>
  Writes data to the buffer. Newline indicates end of data. 

* clearbuf
  Clears the contents of the buffer.

* batch <size>
  Sets the batch size (default 1024).

* quit
  Quits to the uPython REPL

* reboot
  Calls `machine.reset()` to reboot the uPython device.

* mkdir <path>
  Creates a directory at the specified path

* rmdir <path>
  Removes the directory at the specified path
