# This is the stub program which is downloaded to the uPython device. It receives commands from the host via stdin (REPL UART link).
# Code formatting will be a little off-kilter because it needs to conform to REPL input syntax, not normal file syntax.

import os

runFlag = True
while runFlag:
    cmdText = input('\nready~')
    cmd, *params = cmdText.strip().split()
    if cmd == 'list':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: print('\n'.join(os.listdir(params[0])))
        except: print('~~error:bad path'); continue
    elif cmd == 'read':
        if len(params) < 1:
            print('~~error:missing params'); continue
        try: file = open(params[0], 'rb'); data = file.read(); file.close()
        except: print('~~error:bad path'); continue
        print('~~expect:{}'.format(len(data)))
        print(''.join(['{:02X}'.format(d) for d in data]))
        print('~~complete:')
        
    elif cmd == 'write':
        pass
    elif cmd == 'quit':
        runFlag = False
        print('quitting')
    else:
        print('~~error:bad command')

