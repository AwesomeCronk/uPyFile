import os, shutil, sys

installDir = os.path.expandvars('%LOCALAPPDATA%\\Programs\\uPyFile')
downloadDir = os.path.dirname(os.path.realpath(__file__))
configFiles = []
installFiles = ['LICENSE', 'README.md', 'uPyFile.exe']

_version = '1.0.0'

def version():
    print('Using uPyFile installer version {}.'.format(_version))

if len(sys.argv) > 1:
    if sys.argv[1] == 'version':
        version()
else:
    #Check if %LOCALAPPDATA%\Programs\uPyFile exists
    #if so, delete it
    if os.path.exists(installDir):
        print('Removing install directory.')
        shutil.rmtree(installDir)

    #Create installDir
    print('Creating install directory.')
    os.mkdir(installDir)

    #copy the necessary files to installDir
    for file in installFiles:
        print('Copying {} to {} ... '.format(file, installDir), end = '')
        shutil.copy(file, installDir)
        print('Done.')