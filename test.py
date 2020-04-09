import serial
serialPort = serial.Serial(
                           port = "COM3",
                           baudrate = 115200,
                           bytesize = 8,
                           timeout = 2,
                           stopbits = serial.STOPBITS_ONE
                          )

test = True

while(True):
    if serialPort.in_waiting > 0:
        sString = serialPort.readline()
        print('DEVICE: {}'.format(sString))
        if sString == b'>>> ':
            print('HOST: Identfied REPL prompt.')
            if test:
                serialPort.write(b"print('hello world!')\r\n")
                test = False