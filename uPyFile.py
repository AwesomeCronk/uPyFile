import sys, serial, time

_version = '1.4.0'

class fileHandler():
    def __init__(self, comPort, baud = 115200, timeout = 2, stopBits = 1, verbose = False):
        self.enableDebugging = True
        self.verbose = verbose
        self.vbPrint('Opening serial port...', end = ' ')
        self.serialPort = serial.Serial(port = comPort,
                                        baudrate = baud,
                                        bytesize = 8,
                                        timeout = timeout,
                                        stopbits = stopBits)
        self.vbPrint('Done\nRebooting device...', end = ' ')
        self.serialPort.write(b'\x03')           #send the stop code
        self.waitForREPL()
        self.vbPrint('Done.')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def debugComputer(self, debugData):
        if self.enableDebugging:
            print('COMPUTER: {}'.format(debugData))

    def debugDevice(self, debugData):
        if self.enableDebugging:
            print('DEVICE: {}'.format(debugData))

    def vbPrint(self, text, end = '\n'):
        if self.verbose:
            print(text, end = end)

    def waitForREPL(self):
        devOutput = b''                     #wait for the REPL prompt
        while(devOutput != b'>>> '):
            if self.serialPort.in_waiting > 0:
                devOutput = self.serialPort.readline()
                #self.debugDevice(devOutput)

    def read(self, fileNameDev, _print = True):
        self.vbPrint('Sending read command...', end = ' ')
        cmdText = "fileDev = open('{}', 'rb')\r\nfor i in fileDev.read():\r\nprint(hex(i), end = ' ')\r\n\x7f\r\nfileDev.close()".format(fileNameDev)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        #self.debugComputer(dataToSend)

        self.vbPrint('Done.\nReading response...')
        deviceOutput = b''
        dataReceived = self.serialPort.read(1024)
        while dataReceived:
            deviceOutput += dataReceived
            dataReceived = self.serialPort.read(1024)
        #self.debugDevice(deviceOutput)
        self.vbPrint('Done.\nParsing response...', end = ' ')
        data = b''
        for i in deviceOutput.decode('UTF-8', errors = 'ignore').split('\r\n')[-1][0:-20].split(' '):       #Get a list of bytes in '0xab' format
            data += int(i, base = 16).to_bytes(1, 'little')     #convert to raw data and add to data variable
        self.vbPrint('Done.')
        if _print:
            print('Contents of {} are:'.format(fileNameDev))
            print(data.decode('UTF-8', errors = 'ignore'))      #print text version
        else:
            return data

    def push(self, fileNameDev, fileNamePC):
        self.vbPrint('Reading file data on PC...', end = ' ')
        with open(fileNamePC, 'rb') as filePC:
            fileData = str(filePC.read())
            #print('fileData: {}'.format(fileData))
        self.vbPrint('Done.\nSending write command...')
        cmdText = "fileDev = open('{}', 'wb')\r\nfileDev.write({})\r\nfileDev.close()\r\n".format(fileNameDev, fileData)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        #self.debugComputer(dataToSend)
        self.vbPrint('Done.')
        #self.waitForREPL()
        #self.close()

    def pull(self, fileNameDev, fileNamePC):
        data = self.read(fileNameDev, _print = False)
        self.vbPrint('Writing data to file...', end = ' ')
        with open(fileNamePC, 'wb') as filePC:
            filePC.write(data)
        self.vbPrint('Done.')

    def list(self, dirDev):
        self.vbPrint('Sending list command...', end = ' ')
        cmdText = "import os\r\nos.listdir('{}')\r\n".format(dirDev)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        #self.debugComputer(dataToSend)
        self.vbPrint('Done.\nReading response...', end = ' ')
        dataReceived = self.serialPort.read(1024)
        #self.debugDevice(dataReceived)
        self.vbPrint('Done.\nParsing response...')
        listing = ''
        for i in dataReceived.decode('UTF-8', errors = 'ignore').split('\r\n')[-2][2:-2].split("', '"):
            listing += i
            listing += '\n'
        self.vbPrint('Done.')
        print('Contents of directory {} are:'.format(dirDev))
        print(listing)
        #self.close()

    def close(self):
        self.vbPrint('Closing serial port.')
        self.serialPort.close()

if __name__ == '__main__':
    #get operation and parameters from sys.argv
    #call run with the needed parameters
    #if no optional names are provided, substitute them with the required names
    if '-v' in sys.argv or '--verbose' in sys.argv:
        verbose = True
    else:
        verbose = False

    with fileHandler(sys.argv[1], verbose = verbose) as handler:
        action = sys.argv[2]
        #print(action)
        if action == 'read':
            handler.read(sys.argv[3])
        elif action == 'push':
            handler.push(sys.argv[3], sys.argv[4])
        elif action == 'pull':
            handler.pull(sys.argv[3], sys.argv[4])
        elif action == 'ls' or action == 'list':
            handler.list(sys.argv[3])
        elif action == 'version':
            print('Using uPyFile version {}'.format(_version))