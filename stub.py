# This is the stub program which is downloaded to the uPython device. It receives commands from the host via stdin (REPL UART link).

import os, machine

buffer = b''
batch = 1024

runFlag = True
while runFlag:
    cmdText = input('\nready~')
    cmd, *params = cmdText.strip().split()
    print('~~recvd:')

    if cmd == 'list':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: buffer = '\n'.join(os.listdir(params[0])).encode()
        except: print('~~error:bad path'); continue
        print('~~complete:')

    elif cmd == 'read':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: file = open(params[0], 'rb'); buffer = file.read(); file.close()
        except: print('~~error:bad path'); continue
        print('~~complete:')

    elif cmd == 'write':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: file = open(params[0], 'wb'); null = file.write(buffer); file.close(); buffer = b''
        except: print('~~error:bad path'); continue
        print('~~complete:')

    elif cmd == 'readbuf':
        if len(buffer):
            data = buffer[0:batch]
            buffer = buffer[batch:]
            print(''.join(['{:02X}'.format(d) for d in data]))
            print('~~complete:')
        else:
            print('~~error:no data'); continue

    elif cmd == 'writebuf':
        if len(params) < 1:
            print('~~error:missing params'); continue
        dataHex = params[0]
        while len(dataHex):
            buffer += int('0x' + dataHex[0:2]).to_bytes(1, 'big')
            dataHex = dataHex[2:]
        print('~~complete:')

    elif cmd == 'clearbuf':
        buffer = b''
        print('~~complete:')

    elif cmd == 'batch':
        batch = int(params[0])
        print('~~complete:')

    elif cmd == 'quit':
        runFlag = False
        print('~~complete:')

    elif cmd == 'reboot':
        print('~~complete:')
        machine.reset()

    else:
        print('~~error:bad command')

