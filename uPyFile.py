import serial, argparse

_version = '2.0.0'

class fileHandler():
    def __init__(self):
        self.debug = True
        self.verbose = True
        self.portOpen = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


    # Debug methods (to be replaced with logging calls)
    def debugComputer(self, debugData):
        if self.debug:
            print('COMPUTER: {}'.format(debugData))

    def debugDevice(self, debugData):
        if self.debug:
            print('DEVICE: {}'.format(debugData))

    def vbPrint(self, text, end = '\n'):
        if self.verbose:
            print(text, end = end)


    # Serial port management
    def open(self, port, baud = 115200, timeout = 2, stopBits = 1):
        self.vbPrint('Opening serial port...', end = ' ')
        self.serialPort = serial.Serial(port = port,
                                        baudrate = baud,
                                        bytesize = 8,
                                        timeout = timeout,
                                        stopbits = stopBits)
        self.portOpen = True

    def waitForREPL(self):
        devOutput = b''                     #wait for the REPL prompt
        while(devOutput != b'>>> '):
            if self.serialPort.in_waiting > 0:
                devOutput = self.serialPort.readline()
                self.debugDevice(devOutput)

    def close(self):
        if self.portOpen:
            self.vbPrint('Closing serial port...', end = ' ')
            self.serialPort.close()
            self.vbPrint('Done')
        else:
            self.vbPrint('Serial port already closed')


    # Command implementation
    def init(self, args):
        self.vbPrint('Done\nRebooting device...', end = ' ')
        self.serialPort.write(b'\x03')           #send the stop code
        self.waitForREPL()
        self.vbPrint('Done.')

    def read(self, args, _print = True):
        self.vbPrint('Sending read command...', end = ' ')
        cmdText = "fileDev = open('{}', 'rb')\r\nfor i in fileDev.read():\r\nprint(hex(i), end = ' ')\r\n\x7f\r\nfileDev.close()".format(args.file)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        self.debugComputer(dataToSend)

        self.vbPrint('Done.\nReading response...')
        deviceOutput = b''
        dataReceived = self.serialPort.read(1024)
        while dataReceived:
            deviceOutput += dataReceived
            dataReceived = self.serialPort.read(1024)
        self.debugDevice(deviceOutput)
        self.vbPrint('Done.\nParsing response...', end = ' ')
        data = b''
        for i in deviceOutput.decode('UTF-8', errors = 'ignore').split('\r\n')[-1][0:-20].split(' '):       #Get a list of bytes in '0xab' format
            data += int(i, base = 16).to_bytes(1, 'little')     #convert to raw data and add to data variable
        self.vbPrint('Done.')
        if _print:
            print('Contents of {} are:'.format(args.file))
            print(data.decode('UTF-8', errors = 'ignore'))      #print text version
        else:
            return data

    def push(self, args):
        self.vbPrint('Reading file data on PC...', end = ' ')
        with open(args.infile, 'rb') as filePC:
            fileData = str(filePC.read())
            #print('fileData: {}'.format(fileData))
        self.vbPrint('Done.\nSending write command...')
        cmdText = "fileDev = open('{}', 'wb')\r\nfileDev.write({})\r\nfileDev.close()\r\n".format(args.outfile, fileData)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        self.debugComputer(dataToSend)
        self.vbPrint('Done.')
        self.waitForREPL()

    def pull(self, args):
        data = self.read(args.infile, _print = False)
        self.vbPrint('Writing data to file...', end = ' ')
        with open(args.outfile, 'wb') as filePC:
            filePC.write(data)
        self.vbPrint('Done.')

    def list(self, args):
        self.vbPrint('Sending list command...', end = ' ')
        cmdText = "import os\r\nos.listdir('{}')\r\n".format(args.dir)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        self.debugComputer(dataToSend)
        self.vbPrint('Done.\nReading response...', end = ' ')
        dataReceived = self.serialPort.read(1024)
        self.debugDevice(dataReceived)
        self.vbPrint('Done.\nParsing response...')
        listing = ''
        for i in dataReceived.decode('UTF-8', errors = 'ignore').split('\r\n')[-2][2:-2].split("', '"):
            listing += i
            listing += '\n'
        self.vbPrint('Done.')
        print('Contents of directory {} are:'.format(args.dir))
        print(listing)

if __name__ == '__main__':
    with fileHandler() as handler:
        rootParser = argparse.ArgumentParser(prog='uPyFile', description='A file transfer utility for MicroPython devices')
        rootParser.add_argument(
            'device',
            help='Device to interact with',
            type=str
        )
        rootParser.add_argument(
            '--verbose',
            '-v',
            help='Enable verbose output',
            action='store_true'
        )

        subParsers = rootParser.add_subparsers(dest='command')
        subParsers.required = True

        initParser = subParsers.add_parser('init', help='Initialize a device')
        initParser.set_defaults(function=handler.init)

        readParser = subParsers.add_parser('read', help='Read a file from a device')
        readParser.set_defaults(function=handler.read)
        readParser.add_argument(
            'file',
            help='File to read',
            type=str
        )

        pushParser = subParsers.add_parser('push', help='Push a file to a device')
        pushParser.set_defaults(function=handler.push)
        pushParser.add_argument(
            'infile',
            help='File on PC to push',
            type=str
        )
        pushParser.add_argument(
            'outfile',
            help='File on device to push to',
            type=str
        )

        pullParser = subParsers.add_parser('pull', help='Pull a file from a device')
        pullParser.set_defaults(function=handler.pull)
        pullParser.add_argument(
            'infile',
            help='File on device to pull',
            type=str
        )
        pullParser.add_argument(
            'outfile',
            help='File on PC to pull to',
            type=str
        )

        listParser = subParsers.add_parser('list', help='List a directory on a device')
        listParser.set_defaults(function=handler.list)
        listParser.add_argument(
            'dir',
            help='Directory to list',
            type=str
        )

        args = rootParser.parse_args()


        handler.open(args.device)   # Make the serial connection
        args.function(args)         # Run the command

        # if action == 'init':
        #     handler.initDevice()
        # elif action == 'read':
        #     handler.read(sys.argv[3])
        # elif action == 'push':
        #     handler.push(sys.argv[3], sys.argv[4])
        # elif action == 'pull':
        #     handler.pull(sys.argv[3], sys.argv[4])
        # elif action == 'ls' or action == 'list':
        #     handler.list(sys.argv[3])
        # elif action == 'version':
        #     print('Using uPyFile version {}'.format(_version))
