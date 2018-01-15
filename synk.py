import os
import socket
import hashlib

VERSION = '0.2 beta'
RHOST = 'narexium.com'
UPLINK = 4090
DOWNLINK = 4091
PROJECTFOLDER = '/home/k4yt3x/Projects/Python/uncategorized'


def sha256sum(target):
    sha256 = hashlib.sha256()
    with open(target, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def printIcon():
    print(' ____ ___  _ _      _  __')
    print('/ ___\\\\  \\/// \\  /|/ |/ /')
    print('|    \\ \\  / | |\\ |||   /')
    print('\\___ | / /  | | \\|||   \\')
    print('\\____//_/   \\_/  \\|\\_|\\_\\')
    print('\nWelcome Using Synk ' + VERSION)


def recvData(conn):
    received = ""
    while True:
        data = conn.recv(4096)
        received += data.decode('utf-8')
        if len(data) < 4096:
            break
    return received


def writeFile(filename, content):
    with open(filename, 'w') as tf:
        for line in content:
            tf.write(line + '\n')
    tf.close()


def upSynk():
    for file in os.listdir(PROJECTFOLDER):
        if os.path.isdir(file):
            print(file + ' is a directory, skipping')
            continue
        else:
            sock0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock0.connect((RHOST, UPLINK))
            sendBuffer = file + '\n'
            filename = os.path.join(PROJECTFOLDER, file)
            with open(filename, 'r') as target:
                for line in target:
                    sendBuffer += line
            sock0.send(sendBuffer.encode('utf-8'))
            sock0.close()


def downSynk():
    while True:
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.connect((RHOST, DOWNLINK))
        try:
            sock1.connect((RHOST, DOWNLINK))
        except BrokenPipeError:
            continue
        except ConnectionRefusedError:
            continue
        except OSError:
            pass
        received = recvData(sock1)
        print(received)
        if received == 'RST':
            break
        received = received.split('\n')
        filename = received[0]
        received.pop(0)
        writeFile(PROJECTFOLDER + filename, received)
        sock1.close()
    sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


while True:
    upSynk()
    sock0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock0.connect((RHOST, UPLINK))
    sock0.send('RST'.encode('utf-8'))
    downSynk()
