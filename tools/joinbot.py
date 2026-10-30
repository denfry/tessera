"""Minimal offline-mode 26.3 client: handshake -> login -> configuration -> play, then idles answering keep-alives."""
import os
import socket, struct, sys, time, uuid, zlib

PROTO = 777
HOST, PORT = '127.0.0.1', int(sys.argv[1])
NAME = sys.argv[2]
STAY = float(sys.argv[3])
SPAM_FINISH = int(sys.argv[4]) if len(sys.argv) > 4 else 0
# JOINBOT_SCOREBOARD=1: follow team and objective packets like a client and report anything out of order
CHECK_SCOREBOARD = os.environ.get('JOINBOT_SCOREBOARD') == '1'


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


def read_string(b, i):
    n, i = read_varint_buf(b, i)
    return b[i:i + n].decode('utf-8'), i + n


def nbt_texts(b):
    """Strings of a network NBT text component, in order (enough to read chat)."""
    out = []

    def payload(t, i):
        if t in (1,): return i + 1
        if t == 2: return i + 2
        if t in (3, 5): return i + 4
        if t in (4, 6): return i + 8
        if t == 7: return i + 4 + struct.unpack('>i', b[i:i + 4])[0]
        if t == 8:
            n = struct.unpack('>H', b[i:i + 2])[0]
            out.append(b[i + 2:i + 2 + n].decode('utf-8', 'replace'))
            return i + 2 + n
        if t == 9:
            et, n = b[i], struct.unpack('>i', b[i + 1:i + 5])[0]
            i += 5
            for _ in range(n): i = payload(et, i)
            return i
        if t == 10:
            while b[i] != 0:
                et = b[i]; n = struct.unpack('>H', b[i + 1:i + 3])[0]
                key = b[i + 3:i + 3 + n].decode('utf-8', 'replace')
                before = len(out)
                i = payload(et, i + 3 + n)
                if et == 8 and key != 'text': del out[before:]
            return i + 1
        if t == 11: return i + 4 + 4 * struct.unpack('>i', b[i:i + 4])[0]
        if t == 12: return i + 4 + 8 * struct.unpack('>i', b[i:i + 4])[0]
        raise ValueError(t)
    try:
        payload(b[0], 1)
    except Exception:
        pass
    return ''.join(out)


class Scoreboard:
    def __init__(self):
        self.teams, self.objectives = set(), set()
        self.counts = {'team': 0, 'objective': 0, 'score': 0}
        self.errors = []

    def handle(self, pid, data):
        if pid == 111:  # set_player_team: name, method (0 add, 1 remove, 2 change, 3 join, 4 leave)
            name, i = read_string(data, 0)
            self.counts['team'] += 1
            self.track(self.teams, 'team', name, data[i], (0,), (1,))
        elif pid == 108:  # set_objective: name, method (0 add, 1 remove, 2 change)
            name, i = read_string(data, 0)
            self.counts['objective'] += 1
            self.track(self.objectives, 'objective', name, data[i], (0,), (1,))
        elif pid == 112:  # set_score: owner, objective
            _, i = read_string(data, 0)
            objective, _ = read_string(data, i)
            self.counts['score'] += 1
            if objective not in self.objectives:
                self.errors.append('score for unknown objective ' + objective)

    def track(self, known, kind, name, method, adds, removes):
        if method in adds:
            if name in known:
                self.errors.append('%s %s added twice' % (kind, name))
            known.add(name)
        elif name not in known:
            self.errors.append('%s %s changed before it was added (method %d)' % (kind, name, method))
        elif method in removes:
            known.discard(name)

    def report(self):
        print('SCOREBOARD packets %s, teams now %d, objectives now %d, errors %d'
              % (self.counts, len(self.teams), len(self.objectives), len(self.errors)))
        for e in self.errors[:20]:
            print('SCOREBOARD ERROR', e)


board = Scoreboard() if CHECK_SCOREBOARD else None


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
        elif pid == 60:  # open_screen: container id, menu type, title component
            cid, i = read_varint_buf(data)
            mtype, i = read_varint_buf(data, i)
            print('SCREEN: type %d %s' % (mtype, nbt_texts(data[i:])), flush=True)
        elif pid == 124:  # system_chat: text component, overlay
            print('CHAT:', nbt_texts(data), flush=True)
        elif pid == 32:
            print('PLAY DISCONNECT', data[:300]); board and board.report(); sys.exit(1)
        elif board:
            board.handle(pid, data)
        if joined_at and time.time() - joined_at > STAY:
            print('stayed %.0fs, leaving' % STAY); board and board.report(); sys.exit(0)
