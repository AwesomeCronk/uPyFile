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
        except Exception as E: print('~~error:{}'.format(repr(E))); continue

        print('~~complete:')

    elif cmd == 'ilist':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: listing = os.ilistdir(params[0])
        except Exception as E: print('~~error:{}'.format(repr(E))); continue

        entries = []
        # No MicroPython device will likely ever be able to surpass a few GB files, but just to be safe...
        suffixes = ('B', 'kB', 'MB', 'GB', 'TB', 'PB')
        sizeDiv = 1024
        itemNameLen = 0
        for entry in listing:
            if entry[1] == 0x8000: itemType = 'f'
            elif entry[1] == 0x4000: itemType = 'd'
            else: itemType = '?'

            itemName = entry[0]
            itemNameLen = max(itemNameLen, len(itemName))

            if len(entry) >= 4 and itemType == 'f':
                itemSize = entry[3]
                s = 0
                while itemSize >= sizeDiv:
                    itemSize //= sizeDiv
                    s += 1
                itemSize = str(itemSize) + suffixes[s]

            else:
                itemSize = '---'

            entries.append((itemType, itemName, itemSize))

        for e, entry in enumerate(entries):
            itemType, itemName, itemSize = entry
            entries[e] = '{} : {}{} : {}'.format(itemType, itemName, ' ' * (itemNameLen - len(itemName)), itemSize)

        buffer += '\n'.join(entries).encode()

        print('~~complete:')

    elif cmd == 'read':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: file = open(params[0], 'rb'); buffer = file.read(); file.close()
        except Exception as E: print('~~error:{}'.format(repr(E))); continue
        print('~~complete:')

    elif cmd == 'write':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: file = open(params[0], 'wb'); null = file.write(buffer); file.close(); buffer = b''
        except Exception as E: print('~~error:{}'.format(repr(E))); continue
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

    elif cmd == 'mkdir':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: os.mkdir(params[0])
        except Exception as E: print('~~error:{}'.format(repr(E))); continue
        print('~~complete:')

    elif cmd == 'rmdir':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: os.rmdir(params[0])
        except Exception as E: print('~~error:{}'.format(repr(E))); continue
        print('~~complete:')

    else:
        print('~~error:bad command')

