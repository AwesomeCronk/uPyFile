import argparse, logging, serial, time


_version = '2.0.1'
batchSize = 1024
debug = True
verbose = True
portOpen = False
pcLog = logging.getLogger('PC')
devLog = logging.getLogger('DEV')
port = None


# Serial port management
def openPort(portName, baud = 115200, timeout = 0.2, stopBits = 1):
    global portOpen, port
    pcLog.debug('Opening serial port')
    port = serial.Serial(
        port = portName,
        baudrate = baud,
        bytesize = 8,
        timeout = timeout,
        stopbits = stopBits
    )
    portOpen = True

def closePort():
    if portOpen:
        pcLog.debug('Closing serial port')
        port.close()
    else:
        pcLog.debug('Serial port already closed')

def waitFor(line, shush=False):
    pcLog.info('Waiting for {}'.format(line))
    devOutput = b''
    while devOutput != line:
        if port.in_waiting > 0:
            devOutput = port.readline()
            # Clutters debug when the stub is sent, thus the shush flag
            if not shush: devLog.debug(devOutput)
        else:
            time.sleep(0.05)
    pcLog.info('Done waiting')

def checkResponse():
    respRaw = port.readline().strip()
    devLog.debug(respRaw)
    resp = respRaw.split(b':')
    if resp[0] == b'~~error': devLog.error(resp[1]); exit(1)
    elif resp[0] != b'~~complete': devLog.error('Unexpected response: {}'.format(respRaw)); exit(1)


# Command implementation
def cmd_init(args):
    pcLog.debug('Compiling stub')
    with open('stub.py', 'rb') as stubFile: stub = stubFile.read().replace(b'\n', b'\r\n')
    
    print('Initializing device')
    port.write(b'\x03')     # Ctrl+C
    waitFor(b'>>> ')
    port.write(b'\x05')     # Ctrl+E?
    port.write(stub)
    port.write(b'\x04')     # Ctrl+D?
    # pcLog.debug(stub.decode())
    pcLog.info('Sent stub')
    
    cmd = ('batch {}\r\n'.format(batchSize)).encode()
    port.write(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n', shush=True)
    checkResponse()

def cmd_read(args):
    # Stub commands:
    # read file
    # readbuf
    # ...

    # Send read command
    cmd = b'read ' + args.file.encode() + b'\r\n'
    port.write(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n')
    checkResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        port.write(cmd)
        pcLog.debug(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = port.readline()
        devLog.debug(respRaw)
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = port.readline()
        devLog.debug(respRaw)
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]

    print(data.decode('UTF-8', errors = 'ignore'))
    
def cmd_push(args):
    with open(args.infile, 'rb') as infile: data = infile.read()
    
    # Stub commands:
    # writebuf
    # ...
    # write file

    while len(data):
        # Encode data
        dataHex = ''
        dataBatch = data[0:batchSize]; data = data[batchSize:]
        for i in dataBatch:
            dataHex += '{:02X}'.format(i)
        dataHex = dataHex.encode()

        # Send writebuf command
        cmd = b'writebuf ' + dataHex + b'\r\n'
        port.write(cmd)
        pcLog.debug(cmd)
        waitFor(b'~~recvd:\r\n')
        checkResponse()

    # Send write command
    cmd = b'write ' + args.file + b'\r\n'
    port.write(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n')
    checkResponse()

def cmd_pull(args):
    logging.info('Sending read command')
    cmdText = '\r\n'.join([
        "fileDev = open('{}', 'rb')".format(args.infile),
        "for i in fileDev.read(): print(hex(i))",
        "",
        "fileDev.close()",
        ""
        ])
    dataToSend = bytes(cmdText, 'UTF-8')
    self.port.write(dataToSend)
    self.pcLog.debug(dataToSend)

    logging.info('Reading response...')
    deviceOutput = b''
    dataReceived = self.port.read(readLimit)
    while dataReceived:
        deviceOutput += dataReceived
        dataReceived = self.port.read(readLimit)
    self.devLog.debug(deviceOutput)
    logging.info('Parsing response')
    data = b''
    for i in deviceOutput.decode('UTF-8', errors = 'ignore').split('\r\n')[3:]:       #Get a list of bytes in '0xab' format
        if i[0:4] == '>>> ': break
        logging.debug(repr(i)); data += int(i, base = 16).to_bytes(1, 'little')     #convert to raw data and add to data variable
    
    logging.info('Writing data to file')
    with open(args.outfile, 'wb') as filePC:
        filePC.write(data)

def cmd_list(args):
    logging.info('Sending list command')
    cmdText = '\r\n'.join([
        "import os",
        "for item in os.listdir('{}'): print(item)".format(args.dir),
        "",
        ""
    ])
    dataToSend = bytes(cmdText, 'UTF-8')
    self.port.write(dataToSend)
    self.pcLog.debug(dataToSend)
    logging.info('Reading response')
    dataReceived = self.port.read(readLimit)
    self.devLog.debug(dataReceived)
    logging.info('Parsing response')
    listing = ''
    for i in dataReceived.decode('UTF-8', errors = 'ignore').split('\r\n')[3:]:
        if i == '>>> ': break
        listing += i
        listing += '\n'
    print('Contents of directory {} are:'.format(args.dir))
    print(listing)


# Main section
if __name__ == '__main__':
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
    initParser.set_defaults(function=cmd_init)

    readParser = subParsers.add_parser('read', help='Read a file from a device')
    readParser.set_defaults(function=cmd_read)
    readParser.add_argument(
        'file',
        help='File to read',
        type=str
    )

    pushParser = subParsers.add_parser('push', help='Push a file to a device')
    pushParser.set_defaults(function=cmd_push)
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
    pullParser.set_defaults(function=cmd_pull)
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
    listParser.set_defaults(function=cmd_list)
    listParser.add_argument(
        'dir',
        help='Directory to list',
        type=str
    )

    args = rootParser.parse_args()


    if args.verbose: logging.basicConfig(level=logging.DEBUG)
    else: logging.basicConfig(level=logging.WARNING)

    try:
        openPort(args.port, baud=args.baud, timeout=args.timeout)   # Make the serial connection
        args.function(args)     # Run the command
    finally:
        closePort()