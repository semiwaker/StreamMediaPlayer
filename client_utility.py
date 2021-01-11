import socket
import asyncio
import threading
import copy


class MediaBuffer:
    def __init__(self, max_size, fetch_size):
        self.buf = [{'seq': -1, 'data': b'', 'start': 0}]
        self.cur = 0
        self.max_size = max_size
        self.file_name = ""
        self.fetch_size = fetch_size
        self.retain_size = 4
        self.writer = None
        self.reader = None
        self.wr_lock = asyncio.Lock()

        self.cur_byte = 0

        self.paused = False

        self.total = 0

        self.reading = True
        self.playing = asyncio.Event()
        self.eof = asyncio.Event()

        self.host = None
        self.port = None

        self.buf_lock = threading.Lock()
        self.cv = threading.Condition(self.buf_lock)

    def set_writer(self, writer):
        self.writer = writer

    def set_reader(self, reader):
        self.reader = reader

    def set_host_port(self, host, port):
        self.host = host
        self.port = port

    async def get_file_names(self):
        async with self.wr_lock:
            self.writer.write(b'list\n')
            await self.writer.drain()
            lines = await self.reader.readline()
            lines = int(str(lines, encoding='utf-8'))
            names = []
            for i in range(lines):
                name = await self.reader.readline()
                name = name.strip()
                name = str(name, encoding='utf-8')
                names.append(name)
        return names

    def set_name(self, file_name):
        self.file_name = file_name

    async def open(self):
        cnt = 0
        self.reading = True
        async with self.wr_lock:
            while cnt < 3:
                self.writer.write(bytes('file %s %s %d\n' %
                                        (self.file_name, self.host, self.port),
                                        encoding="utf-8"))
                msg = (await self.reader.readline()).strip().split()
                print(msg)
                if msg[0] == b'no':
                    cnt += 1
                elif msg[0] == b'ok':
                    self.playing.set()
                    self.eof.clear()
                    self.cur = 1
                    self.cur_byte = 0
                    self.paused = False
                    self.buf = [{'seq': -1, 'data': b'', 'start': 0}]
                    self.total = int(str(msg[1], encoding='utf-8'))
                    break

    def insert(self, seq, data):
        with self.cv:
            last_ts = self.buf[-1]['seq']
            if self.buf[-1]['start'] is not None:
                end = self.buf[-1]['start'] + len(self.buf[-1]['data'])
            else:
                end = None
            if last_ts < seq:
                self.buf += [
                    {
                        'seq': i,
                        'data': None,
                        'start': None if i != last_ts+1 else end
                    }
                    for i in range(last_ts+1, seq+1)
                ]
            first_ts = self.buf[0]['seq']
            x = seq-first_ts
            self.buf[x]['data'] = data
            while (len(self.buf) > x+1 and self.buf[x]['start'] is not None
                    and self.buf[x+1]['start'] is None):
                self.buf[x+1]['start'] = (self.buf[x]['start'] +
                                          len(self.buf[x]['data']))
                if (self.cur == x and
                    self.cur_byte >= self.buf[x]['start']
                        + len(self.buf[x]['data'])):
                    self.cur += 1
                x += 1
            # print("Inserted")
            # for b in self.buf:
            #     print(b['seq'], b['start'], len(b['data']))
            if self.available():
                self.cv.notify()

    def available(self):
        return (self.cur == self.total or
                self.cur < len(self.buf) and
                self.buf[self.cur]['data'] is not None and
                self.buf[self.cur]['start'] is not None)

    def fetch(self, length):
        with self.cv:
            self.cv.wait_for(self.available)

            if self.cur == self.total:
                return b''

            start = self.buf[self.cur]['start']
            end = start + len(self.buf[self.cur]['data'])

            length = min(length, self.fetch_size)

            if end - self.cur_byte < length:
                data = self.buf[self.cur]['data'][self.cur_byte - start:]

                self.cur = self.cur + 1
                if self.cur > 2 * self.retain_size:
                    self.cur -= self.retain_size
                    self.buf = self.buf[self.retain_size:]
            else:
                data = self.buf[self.cur]['data'][
                    self.cur_byte - start:self.cur_byte-start+length]
            self.cur_byte += len(data)
            # print("Fetched", self.cur, self.cur_byte)
            return data

    def seek(self, offset):
        self.cur_byte = offset
        self.cur = 0
        while (self.cur + 1 < len(self.buf) and
               self.buf[self.cur]['start'] is not None and
               self.cur_byte >= self.buf[self.cur]['start'] +
               len(self.buf[self.cur]['data'])
               ):
            self.cur += 1

    def close(self):
        self.playing.clear()
        self.eof.set()
        self.reading = False
