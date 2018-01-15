import os
import socket
import hashlib

VERSION = '0.2 beta'
LHOST = '0.0.0.0'
UPLINK = 4090
DOWNLINK = 4091
PROJECTFOLDER = '/var/projects'


def sha256sum(target):
    sha256 = hashlib.sha256()
    with open(target, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


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


def initSocket():
    global sock0
    global sock1
    sock0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock0.bind((LHOST, UPLINK))
    sock0.listen(10)
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock1.bind((LHOST, DOWNLINK))
    sock1.listen(10)


def upSynk():
    while True:
        socketClient, address = sock0.accept()
        received = recvData(socketClient)
        print(received)
        if received == 'RST':
            break
        received = received.split('\n')
        filename = received[0]
        received.pop(0)
        writeFile(PROJECTFOLDER + filename, received)
        socketClient.close()


def downSynk():
    for file in os.listdir(PROJECTFOLDER):
        if os.path.isdir(file):
            print(file + ' is a directory, skipping')
            continue
        else:
            socketClient, address = sock1.accept()
            sendBuffer = file + '\n'
            filename = os.path.join(PROJECTFOLDER, file)
            with open(filename, 'r') as target:
                for line in target:
                    sendBuffer += line
            socketClient.send(sendBuffer.encode('utf-8'))
            socketClient.close()


initSocket()
while True:
    upSynk()
    downSynk()
    socketClient, address = sock1.accept()
    socketClient.send('RST'.encode('utf-8'))
    socketClient.close()
