import argparse, logging, serial, time


_version = '3.0.0'
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

def readPort(wait=True):
    if wait:
        while port.in_waiting == 0:
            time.sleep(0.05)
    return port.readline()

def writePort(data):
    port.write(data)

def waitFor(line, shush=False):
    pcLog.info('Waiting for {}'.format(line))
    devOutput = b''
    while devOutput != line:
        devOutput = readPort()
        # Clutters debug when the stub is sent, thus the shush flag
        if not shush: devLog.debug(devOutput)
    pcLog.info('Done waiting')

def checkResponse():
    respRaw = readPort().strip()
    devLog.debug(respRaw)
    resp = respRaw.split(b':')
    if resp[0] == b'~~error': devLog.error(resp[1]); exit(1)
    elif resp[0] == b'~~complete': pcLog.debug('Response ok')
    else: pcLog.error('Unexpected response: {}'.format(respRaw)); exit(1)


# Command implementation
def _readFile(file):
    # Stub commands:
    # read file
    # readbuf
    # ...

    # Send read command
    cmd = b'read ' + file.encode() + b'\r\n'
    writePort(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n')
    checkResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        writePort(cmd)
        pcLog.debug(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = readPort()
        devLog.debug(respRaw)
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = readPort()
        devLog.debug(respRaw)
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]
    
    return data

def cmd_init(args):
    pcLog.debug('Compiling stub')
    with open('stub.py', 'rb') as stubFile: stub = stubFile.read().replace(b'\n', b'\r\n')
    
    print('Initializing device')
    writePort(b'\x03')     # Ctrl+C
    waitFor(b'>>> ')
    writePort(b'\x05')     # Ctrl+E?
    writePort(stub)
    writePort(b'\x04')     # Ctrl+D?
    # pcLog.debug(stub.decode())
    pcLog.info('Sent stub')
    
    cmd = ('batch {}\r\n'.format(batchSize)).encode()
    writePort(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n', shush=True)
    checkResponse()

def cmd_read(args):
    data = _readFile(args.file)

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
        writePort(cmd)
        pcLog.debug(cmd)
        waitFor(b'~~recvd:\r\n')
        checkResponse()

    # Send write command
    cmd = b'write ' + args.outfile.encode() + b'\r\n'
    writePort(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n')
    checkResponse()

def cmd_pull(args):
    data = _readFile(args.infile)
    
    with open(args.outfile, 'wb') as filePC:
        filePC.write(data)

def cmd_list(args):
    # Stub commands:
    # list

    # Send the list command
    cmd = b'list ' + args.dir.encode() + b'\r\n'
    writePort(cmd)
    pcLog.debug(cmd)
    waitFor(b'~~recvd:\r\n')
    checkResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        writePort(cmd)
        pcLog.debug(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = readPort()
        devLog.debug(respRaw)
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = readPort()
        devLog.debug(respRaw)
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]
    
    listing = data.decode()

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