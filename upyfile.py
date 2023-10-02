import argparse, logging, os, serial, sys, time


_version = '3.2.1'
bufferSize = 1024   # Buffer size for serial data
batchSize = 1024    # Batch size for command data
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

def readPort(wait=True, shush=False):
    if wait:
        while port.in_waiting == 0:
            time.sleep(0.05)
    data = port.readline()
    # Clutters debug when the stub is sent, thus the shush flag
    if not shush: devLog.debug(data)
    return data

def writePort(data):
    pcLog.debug(data)
    # Write the data in batches to ensure the buffer never overflows
    remaining = data
    while len(remaining) > bufferSize:
        port.write(remaining[0:bufferSize])
        remaining = remaining[bufferSize:]
        port.flush()
    if len(remaining):
        port.write(remaining)
        port.flush()

def waitFor(line, shush=False, dumpOnTraceback=True):
    pcLog.info('Waiting for {}'.format(line))
    devOutput = b''
    tracebackSequence = b'Traceback (most recent call last):\r\n'
    tracebackDoneSequence = b'>>> '
    while devOutput != line:
        devOutput = readPort(shush=shush)
        if dumpOnTraceback and devOutput == tracebackSequence:
            break
    else:   # If loop didn't break, no traceback was caught
        pcLog.info('Done waiting')
        return
    
    devLog.error('Device error')
    traceback = devOutput
    for i in range(10):
        if devOutput == tracebackDoneSequence: break
        devOutput = readPort(shush=shush)
        traceback = traceback + devOutput
    devLog.error('Device traceback:\n{}'.format(traceback.decode('utf-8', errors='replace')))
    sys.exit(1)
    

def verifyResponse():
    respRaw = readPort().strip()
    resp = respRaw.split(b':')
    if resp[0] == b'~~error':
        devLog.error(resp[1]); sys.exit(1)

    elif resp[0] == b'~~complete':
        pcLog.debug('Response ok')
    else:
        pcLog.error('Unexpected response: {}'.format(respRaw))

        time.sleep(0.1) # Give the device 100ms to get the rest of the response out
        badResp = b''
        while port.in_waiting > 0:
            badResp = badResp + port.readline()
            time.sleep(0.05)    # Continue waiting each batch for 50ms to get any that's left.

        pcLog.error(badResp)
    
        sys.exit(1)


# Command implementation
def _readFile(file):
    # Stub commands:
    # read file
    # readbuf
    # ...

    # Send read command
    cmd = b'read ' + file.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        writePort(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = readPort()
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = readPort()
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); sys.exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]
    
    return data

def cmd_init(args):
    pcLog.debug('Loading stub')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stub.py'), 'rb') as stubFile: stub = stubFile.read().replace(b'\n', b'\r\n')
    
    print('Initializing device')
    writePort(b'\x03')      # Ctrl+C
    waitFor(b'>>> ')
    writePort(b'\x05')      # Ctrl+E
    writePort(stub)    
    writePort(b'\x04')      # Ctrl+D
    waitFor(b'ready~')
    pcLog.info('Sent stub')
    
    cmd = ('batch {}\r\n'.format(batchSize)).encode()
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

def cmd_cd(args):
    # Stub commands:
    # cd

    # Send cd command
    cmd = b'cd ' + args.dir.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

def cmd_pwd(args):
    # Stub commands:
    # pwd

    # Send pwd command
    cmd = b'pwd\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        writePort(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = readPort()
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = readPort()
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); sys.exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]
    
    print(data.decode())

def cmd_list(args):
    # Stub commands:
    # list

    # Send list command
    cmd = b'list ' + args.dir.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        writePort(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = readPort()
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = readPort()
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); sys.exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]
    
    listing = data.decode()

    print('Contents of directory {} are:'.format(args.dir))
    print(listing)

def cmd_ilist(args):
    # Stub commands:
    # ilist

    # Send ilist command
    cmd = b'ilist ' + args.dir.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

    dataRaw = b''
    while True:
        # Send readbuf command
        cmd = b'readbuf' + b'\r\n'
        writePort(cmd)
        waitFor(b'~~recvd:\r\n')

        # Process response
        respRaw = readPort()
        if respRaw == b'~~error:no data\r\n': pcLog.debug('No data, breaking loop'); break
        else: dataRaw += respRaw.strip()

        respRaw = readPort()
        if respRaw != b'~~complete:\r\n':
            devLog.error('Unexpected response: {}'.format(respRaw)); sys.exit(1)

    # Decode data
    data = b''
    while len(dataRaw):
        data += int('0x' + dataRaw[0:2].decode(), base=16).to_bytes(1, 'big')
        dataRaw = dataRaw[2:]
    
    listing = data.decode()

    print('Contents of directory {} are:'.format(args.dir))
    print(listing)

def cmd_mkdir(args):
    # Stub commands:
    # mkdir

    # Send mkdir command
    cmd = b'mkdir ' + args.path.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

def cmd_rmdir(args):
    # Stub commands:
    # mkdir

    # Send rmdir command
    cmd = b'rmdir ' + args.path.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

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
        waitFor(b'~~recvd:\r\n')
        verifyResponse()

    # Send write command
    cmd = b'write ' + args.outfile.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

def cmd_pull(args):
    data = _readFile(args.infile)
    
    with open(args.outfile, 'wb') as filePC:
        filePC.write(data)

def cmd_ren(args):
    # Stub commands:
    # ren

    # Send ren command
    cmd = b'ren ' + args.old.encode() + b' ' + args.new.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()

def cmd_rm(args):
    # Stub commands:
    # rm

    # Send rm command
    cmd = b'rm ' + args.file.encode() + b'\r\n'
    writePort(cmd)
    waitFor(b'~~recvd:\r\n')
    verifyResponse()


# Main section
if __name__ == '__main__':
    rootParser = argparse.ArgumentParser(prog='uPyFile', description='uPyfile {}: A file transfer utility for MicroPython devices'.format(_version))
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
        '-B',
        '--buffer',
        help='Buffer size',
        type=int,
        default=1024
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

    cdParser = subParsers.add_parser('cd', help='Change the working directory')
    cdParser.set_defaults(function=cmd_cd)
    cdParser.add_argument(
        'dir',
        help='What to change the working directory to',
        type=str
    )

    pwdParser = subParsers.add_parser('pwd', help='Print the working directory')
    pwdParser.set_defaults(function=cmd_pwd)

    listParser = subParsers.add_parser('list', help='List a directory on a device (names only)')
    listParser.set_defaults(function=cmd_list)
    listParser.add_argument(
        'dir',
        help='Directory to list',
        type=str
    )

    listParser = subParsers.add_parser('ilist', help='List a directory on a device (names and attributes)')
    listParser.set_defaults(function=cmd_ilist)
    listParser.add_argument(
        'dir',
        help='Directory to list',
        type=str
    )

    mkdirParser = subParsers.add_parser('mkdir', help='Make a directory on a device')
    mkdirParser.set_defaults(function=cmd_mkdir)
    mkdirParser.add_argument(
        'path',
        help='Path at which to create a directory',
        type=str
    )

    rmdirParser = subParsers.add_parser('rmdir', help='Remove a directory on a device')
    rmdirParser.set_defaults(function=cmd_rmdir)
    rmdirParser.add_argument(
        'path',
        help='Path at which to create a directory',
        type=str
    )

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

    renParser = subParsers.add_parser('ren', help='Rename a file or directory')
    renParser.set_defaults(function=cmd_ren)
    renParser.add_argument(
        'old',
        help='File to delete',
        type=str
    )
    renParser.add_argument(
        'new',
        help='File to delete',
        type=str
    )

    rmParser = subParsers.add_parser('rm', help='Remove a file')
    rmParser.set_defaults(function=cmd_rm)
    rmParser.add_argument(
        'file',
        help='File to delete',
        type=str
    )

    args = rootParser.parse_args()


    if args.verbose: logging.basicConfig(level=logging.DEBUG)
    else: logging.basicConfig(level=logging.WARNING)

    bufferSize = args.buffer

    try:
        openPort(args.port, baud=args.baud, timeout=args.timeout)   # Make the serial connection
        args.function(args)     # Run the command
    finally:
        closePort()