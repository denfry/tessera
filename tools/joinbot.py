"""Minimal offline-mode 26.3 client: handshake -> login -> configuration -> play, then idles answering keep-alives."""
import socket, struct, sys, time, uuid, zlib

PROTO = 777
HOST, PORT = '127.0.0.1', int(sys.argv[1])
NAME = sys.argv[2]
STAY = float(sys.argv[3])
SPAM_FINISH = int(sys.argv[4]) if len(sys.argv) > 4 else 0


def varint(n):
    n &= 0xFFFFFFFF
    out = b''
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out += bytes([b | 0x80])
        else:
            return out + bytes([b])


def read_varint_buf(b, i=0):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s; s += 7
        if c < 0x80:
            return r, i


def string(s):
    e = s.encode()
    return varint(len(e)) + e


class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=30)
        self.threshold = -1
        self.buf = b''

    def frame(self, pid, data=b''):
        body = varint(pid) + data
        if self.threshold >= 0:
            if len(body) >= self.threshold:
                body = varint(len(body)) + zlib.compress(body)
            else:
                body = varint(0) + body
        return varint(len(body)) + body

    def send(self, pid, data=b''):
        self.s.sendall(self.frame(pid, data))

    def _read(self, n):
        while len(self.buf) < n:
            c = self.s.recv(65536)
            if not c:
                raise EOFError('server closed the connection')
            self.buf += c
        r, self.buf = self.buf[:n], self.buf[n:]
        return r

    def recv(self):
        r = s = 0
        while True:
            c = self._read(1)[0]
            r |= (c & 0x7F) << s; s += 7
            if c < 0x80:
                break
        body = self._read(r)
        if self.threshold >= 0:
            dlen, i = read_varint_buf(body)
            body = zlib.decompress(body[i:]) if dlen else body[i:]
        pid, i = read_varint_buf(body)
        return pid, body[i:]


c = Conn()
c.send(0, varint(PROTO) + string(HOST) + struct.pack('>H', PORT) + varint(2))
c.send(0, string(NAME) + uuid.uuid3(uuid.NAMESPACE_DNS, 'OfflinePlayer:' + NAME).bytes)
state = 'login'
t0 = time.time()
joined_at = None
while True:
    pid, data = c.recv()
    if state == 'login':
        if pid == 3:
            c.threshold, _ = read_varint_buf(data)
        elif pid == 2:
            c.send(3)
            state = 'config'
            c.send(0, string('en_us') + bytes([8]) + varint(0) + b'\x01' + b'\x7f' + varint(1) + b'\x00' + b'\x01' + varint(0))
        elif pid == 0:
            print('LOGIN DISCONNECT', data[:200]); sys.exit(1)
    elif state == 'config':
        if pid == 15:
            c.send(7, data)  # echo the known packs back
        elif pid == 4:
            c.send(4, data)
        elif pid == 5:
            c.send(5, data)
        elif pid == 2:
            print('CONFIG DISCONNECT', data[:300]); sys.exit(1)
        elif pid == 3:
            frames = c.frame(3) * (1 + SPAM_FINISH)
            c.s.sendall(frames)
            state = 'play'
            print('config finished after %.2fs (sent %d finish packets)' % (time.time() - t0, 1 + SPAM_FINISH))
    else:
        if pid == 50 and joined_at is None:
            joined_at = time.time()
            print('JOINED (play login) after %.2fs' % (joined_at - t0))
        elif pid == 45:
            c.send(28, data)
        elif pid == 32:
            print('PLAY DISCONNECT', data[:300]); sys.exit(1)
        if joined_at and time.time() - joined_at > STAY:
            print('stayed %.0fs, leaving' % STAY); sys.exit(0)
