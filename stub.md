The [stub program](/stub.py) is uploaded to the device when `init` is run. It runs commands to make things a touch easier on the PC end of things whithout increasing the overhead on the device too much.

A few notes:
* All hex data is presented in uppercase, no leading `0x`.
* The stub will print `ready~` when prompting for a command.
* The stub will print `~~recvd:` when a command is received.
* All commands will print `~~error:reason` on an error.
* All commands will print `~~complete:` when finished.

## Commands
* list <path>
  Prints the names of all files and folders in the specified directory, separated by newlines. Returns the error `bad path` if the path is invalid.

* read <path>
  Opens the specified file and reads it's contents into the buffer. Clears existing buffer contents. Returns the error `bad path` if the path is invalid.

* write <path>
  Opens the specified file and writes the contents of the buffer into it. Returns the error `bad path` if the path is invalid.

* readbuf
  Prints out the first so many bytes of the buffer in uppercase hex, up to the configured batch size. Newline indicates end of data.

* writebuf <data>
  Prompts for data in hex, and writes it to the buffer. Newline indicates end of data. 

* clearbuf
  Clears the contents of the buffer.

* batch <size>
  Sets the batch size (default 1024).

* quit
  Quits to the uPython REPL

* reboot
  Calls `machine.reset()` to reboot the uPython device.
