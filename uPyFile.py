import sys, serial, time

_version = '1.2.1'

class fileHandler():
    def __init__(self, comPort, baud = 115200, timeout = 2, stopBits = 1):
        self.enableDebugging = True

        self.serialPort = serial.Serial(port = comPort,
                                        baudrate = baud,
                                        bytesize = 8,
                                        timeout = timeout,
                                        stopbits = stopBits)

        #self.serialPort.write(b'\x03')           #send the stop code
        #self.waitForREPL()

    def __enter__(self):
        pass

    def __exit__(self):
        print('Closing serial port.')
        self.close()

    def debugComputer(self, debugData):
        if self.enableDebugging:
            print('COMPUTER: {}'.format(debugData))

    def debugDevice(self, debugData):
        if self.enableDebugging:
            print('DEVICE: {}'.format(debugData))

    def waitForREPL(self):
        devOutput = b''                     #wait for the REPL prompt
        while(devOutput != b'>>> '):
            if self.serialPort.in_waiting > 0:
                devOutput = self.serialPort.readline()
                #self.debugDevice(devOutput)

    def read(self, fileNameDev):
        cmdText = "fileDev = open('{}', 'rb')\r\nfor i in fileDev.read():\r\nprint(hex(i), end = ' ')\r\n\x7f\r\nfileDev.close()".format(fileNameDev)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        #self.debugComputer(dataToSend)
        deviceOutput = b''
        dataReceived = self.serialPort.read(1024)
        while dataReceived:
            deviceOutput += dataReceived
            dataReceived = self.serialPort.read(1024)
        #self.debugDevice(deviceOutput)
        for i in deviceOutput.decode('UTF-8', errors = 'ignore').split('\r\n')[-1][0:-20].split(' '):       #Get a list of bytes in '0xab' format
            print(int(i, base = 16).to_bytes(1, 'little').decode('UTF-8', errors = 'ignore'), end = '')     #convert to raw data and print


    def push(self, fileNameDev, fileNamePC):
        with open(fileNamePC, 'rb') as filePC:
            fileData = str(filePC.read())
            #print('fileData: {}'.format(fileData))
        cmdText = "fileDev = open('{}', 'wb')\r\nfileDev.write({})\r\nfileDev.close()\r\n".format(fileNameDev, fileData)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        #self.debugComputer(dataToSend)
        self.waitForREPL()
        self.close()

    def pull(self, fileNameDev, fileNamePC):
        print('pulling files is not yet supported')

    def list(self, dirDev):
        print('Listing directory: {}'.format(dirDev))
        cmdText = "import os\r\nos.listdir('{}')\r\n".format(dirDev)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        #self.debugComputer(dataToSend)
        dataReceived = self.serialPort.read(1024)
        #self.debugDevice(dataReceived)
        for i in dataReceived.decode('UTF-8', errors = 'ignore').split('\r\n')[-2][2:-2].split("', '"):
            print(i)
        self.close()

    def close(self):
        self.serialPort.close()

if __name__ == '__main__':
    #get operation and parameters from sys.argv
    #call run with the needed parameters
    #if no optional names are provided, substitute them with the required names
    handler = fileHandler(sys.argv[1])
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