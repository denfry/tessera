"""Minimal RCON client for test servers: rcon.py <port> <password> <command>...  Prints each command and its reply."""
import socket
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def packet(request_id, kind, body):
    data = struct.pack('<ii', request_id, kind) + body.encode('utf-8') + b'\0\0'
    return struct.pack('<i', len(data)) + data


def receive(sock):
    size = struct.unpack('<i', sock.recv(4))[0]
    data = b''
    while len(data) < size:
        data += sock.recv(size - len(data))
    return data[8:-2].decode('utf-8', errors='replace')


def main():
    if len(sys.argv) < 4:
        sys.exit('usage: rcon.py <port> <password> <command>...')
    port, password, commands = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
    sock = socket.create_connection(('127.0.0.1', port))
    sock.settimeout(30)
    sock.send(packet(1, 3, password))
    receive(sock)
    for command in commands:
        sock.send(packet(2, 2, command))
        print('>', command)
        print(receive(sock))


if __name__ == '__main__':
    main()
