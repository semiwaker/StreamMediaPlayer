import asyncio
import math
import threading
import time


class MediaBuffer:
    def __init__(self, max_size):
        self.buf = [{'seq': -1, 'data': None}]
        self.cur = 0
        self.max_size = max_size
        self.file_name = ""
        self.fetch_size = 8
        self.write = None
        self.reader = None

        self.buf_lock = threading.Lock()
        self.cv = threading.Condition(self.buf_lock)

    def set_writer(writer):
        self.writer = writer

    def set_reader(reader):
        self.reader = reader

    async def get_file_names(self):
        writer.write('file')
        line = async reader.readline()
        return line[1:]

    def set_name(self, file_name):
        self.file_name = file_name

    async def open(self):
        writer.write('file %s' % (self.file_name))
        pass

    def insert(self, seq, data):
        with self.buf_lock:
            last_ts = self.buf[-1]['seq']
            if last_ts < seq:
                self.buf += [
                    {'seq': i, 'data': None}
                    for i in range(last_ts+1, seq+1)
                ]
            first_ts = self.buf[0]['seq']
            self.buf[seq-first_ts]['data'] = data
        if self.available():
            with self.cv:
                self.cv.notify()

    def available(self):
        return self.buf[self.cur+1]['data'] is not None

    def fetch(self):
        with self.cv:
            self.cv.wait_for(self.available)

            self.cur = self.cur + 1
            data = self.buf[self.cur]['data']

            if self.cur > self.fetch_size:
                self.cur -= self.fetch_size
                self.buf = self.buf[self.fetch_size:]
            return data

    def seek(self, offset):
        pass

    def close(self):
        pass
