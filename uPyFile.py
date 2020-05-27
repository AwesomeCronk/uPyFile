import sys, serial, time

def run(
        comPort, baud = 115200, timeout = 2, stopBits = 1,
        operation = '', fileNameDev = '', fileNamePC = ''
       ):
    serialPort = serial.Serial(         #instantiate a serial port object
                               port = comPort,
                               baudrate = baud,
                               bytesize = 8,
                               timeout = timeout,
                               stopbits = stopBits
                              )

    serialPort.write(b'\x03')           #send the stop code

    devOutput = b''                     #wait for the REPL prompt
    while(devOutput != b'>>> '):
        if serialPort.in_waiting > 0:
            devOutput = serialPort.readline()
            print('DEVICE: {}'.format(devOutput))

    if operation == 'read':
        #send command to read the file, then remove the buffering stuff from around it
        pass
    elif operation == 'push':
        #open, read, and close the file on the pc, then send the commands to open, write and close a file
        pass
    elif operation == 'pull':
        #send the commands to open, read, and cloase the file, then open, write, and close a file on the pc
        pass

if __name__ == '__main__':
    #get operation and parameters from sys.argv
    #call run with the needed parameters
    #if no optional names are provided, substitute them with the required names