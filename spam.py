import serial
serialPort = serial.Serial(
                           port = "COM3",
                           baudrate = 115200,
                           bytesize = 8,
                           timeout = 2,
                           stopbits = serial.STOPBITS_ONE
                          )

serialPort.write(b'\x03')

while(True):
    if serialPort.in_waiting > 0:
        sString = serialPort.readline()
        print('DEVICE: {}'.format(sString))