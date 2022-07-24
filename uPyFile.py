import argparse, logging, serial

_version = '2.0.0'
readLimit = 4096

class fileHandler():
    def __init__(self):
        self.debug = True
        self.verbose = True
        self.portOpen = False
        self.pcLogger = logging.getLogger('PC')
        self.devLogger = logging.getLogger('DEV')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


    # Serial port management
    def open(self, port, baud = 115200, timeout = 0.2, stopBits = 1):
        logging.info('Opening serial port')
        self.serialPort = serial.Serial(
            port = port,
            baudrate = baud,
            bytesize = 8,
            timeout = timeout,
            stopbits = stopBits
        )
        self.portOpen = True

    def waitForREPL(self):
        devOutput = b''                     #wait for the REPL prompt
        while(devOutput != b'>>> '):
            if self.serialPort.in_waiting > 0:
                devOutput = self.serialPort.readline()
                self.devLogger.debug(devOutput)

    def close(self):
        if self.portOpen:
            logging.info('Closing serial port')
            self.serialPort.close()
        else:
            logging.info('Serial port already closed')


    # Command implementation
    def init(self, args):
        print('Initializing device')
        self.serialPort.write(b'\x03')           #send the stop code
        self.waitForREPL()

    def read(self, args, _print = True):
        logging.info('Sending read command')
        cmdText = '\r\n'.join([
            "fileDev = open('{}', 'rb')".format(args.file),
            "for i in fileDev.read(): print(hex(i))",
            "",
            "fileDev.close()",
            ""
            ])
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        self.pcLogger.debug(dataToSend)

        logging.info('Reading response...')
        deviceOutput = b''
        dataReceived = self.serialPort.read(readLimit)
        while dataReceived:
            deviceOutput += dataReceived
            dataReceived = self.serialPort.read(readLimit)
        self.devLogger.debug(deviceOutput)
        logging.info('Parsing response')
        data = b''
        for i in deviceOutput.decode('UTF-8', errors = 'ignore').split('\r\n')[3:]:       #Get a list of bytes in '0xab' format
            if i[0:4] == '>>> ': break
            logging.debug(repr(i)); data += int(i, base = 16).to_bytes(1, 'little')     #convert to raw data and add to data variable
        if _print:
            print('Contents of {} are:'.format(args.file))
            print(data.decode('UTF-8', errors = 'ignore'))      #print text version
        else:
            return data

    def push(self, args):
        logging.info('Reading file data on PC')
        with open(args.infile, 'rb') as filePC:
            fileData = str(filePC.read())
            #print('fileData: {}'.format(fileData))
        logging.info('Sending write command...')
        cmdText = '\r\n'.join([
            "fileDev = open('{}', 'wb')".format(args.outfile),
            "fileDev.write({})".format(fileData),
            "fileDev.close()",
            ""
        ])
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        self.pcLogger.debug(dataToSend)
        self.waitForREPL()

    def pull(self, args):
        data = self.read(args.infile, _print = False)
        logging.info('Writing data to file')
        with open(args.outfile, 'wb') as filePC:
            filePC.write(data)

    def list(self, args):
        logging.info('Sending list command')
        cmdText = '\r\n'.join([
            "import os",
            "for item in os.listdir('{}'): print(item)".format(args.dir),
            "",
            ""
        ])
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        self.pcLogger.debug(dataToSend)
        logging.info('Reading response')
        dataReceived = self.serialPort.read(readLimit)
        self.devLogger.debug(dataReceived)
        logging.info('Parsing response')
        listing = ''
        for i in dataReceived.decode('UTF-8', errors = 'ignore').split('\r\n')[3:]:
            if i == '>>> ': break
            listing += i
            listing += '\n'
        print('Contents of directory {} are:'.format(args.dir))
        print(listing)

if __name__ == '__main__':
    with fileHandler() as handler:
        rootParser = argparse.ArgumentParser(prog='uPyFile', description='A file transfer utility for MicroPython devices')
        rootParser.add_argument(
            '-p',
            '--port',
            help='Port the device is on',
            type=str
        )
        rootParser.add_argument(
            '-b',
            '--baud',
            help='Baudrate to use',
            type=int,
            default=115200
        )
        rootParser.add_argument(
            '-t',
            '--timeout',
            help='Timeout (in seconds) for serial comms',
            type=float,
            default=0.2
        )
        rootParser.add_argument(
            '-v',
            '--verbose',
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


        if args.verbose: logging.basicConfig(level=logging.DEBUG)
        else: logging.basicConfig(level=logging.WARNING)
        handler.open(args.port, baud=args.baud, timeout=args.timeout)   # Make the serial connection
        args.function(args) # Run the command
