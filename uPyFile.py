import sys, serial, time

class fileHandler():
    def __init__(self, comPort, baud = 115200, timeout = 2, stopBits = 1):
        self.serialPort = serial.Serial(port = comPort,
                                        baudrate = baud,
                                        bytesize = 8,
                                        timeout = timeout,
                                        stopbits = stopBits)

        self.serialPort.write(b'\x03')           #send the stop code
        self.waitForREPL()

    def __enter__(self):
        return

    def __exit__(self):
        self.close()

    def waitForREPL(self):
        devOutput = b''                     #wait for the REPL prompt
        while(devOutput != b'>>> '):
            if self.serialPort.in_waiting > 0:
                devOutput = self.serialPort.readline()
                print('DEVICE: {}'.format(devOutput))

    def read(self, fileNameDev):
        print('reading files not yet supported')

    def push(self, fileNameDev, fileNamePC):
        with open(fileNamePC, 'rb') as filePC:
            fileData = self.padData(filePC.read())
            #print('fileData: {}'.format(fileData))
        cmdText = "fileDev = open('{}', 'wb')\r\nfileDev.write({})\r\nfileDev.close()\r\n".format(fileNameDev, fileData)
        dataToSend = bytes(cmdText, 'UTF-8')
        self.serialPort.write(dataToSend)
        print('COMPUTER: {}'.format(dataToSend))
        self.waitForREPL()

    def pull(self, fileNameDev, fileNamePC):
        print('pulling files not yet supported')

    def padData(self, dataIn):
        return str(dataIn)

    def unpadData(self, dataIn):
        pass

    def close(self):
        self.serialPort.close()

if __name__ == '__main__':
    #get operation and parameters from sys.argv
    #call run with the needed parameters
    #if no optional names are provided, substitute them with the required names
    handler = fileHandler(sys.argv[1])
    action = sys.argv[2]
    if action == 'read':
        handler.read(sys.argv[3])
    elif action == 'push':
        handler.push(sys.argv[3], sys.argv[4])
    elif action == 'pull':
        handler.pull(sys.argv[3], sys.argv[4])