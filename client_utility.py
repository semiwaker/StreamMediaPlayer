import asyncio
import threading


class MediaBuffer:
    def __init__(self, interval, max_size, fetch_size):
        self.buf = [{'timestamp': 0, 'data': None}]
        self.cur = 1
        self.max_size = max_size
        self.interval = interval
        self.fetch_size = fetch_size
        self.file_name = ""
        self.last_data = None

        self.buf_lock = threading.Lock()
        self.cv = threading.Condition(self.buf_lock)

    async def get_file_names(self):
        return [""]

    def set_name(self, file_name):
        self.file_name = file_name

    async def open(self):
        pass

    def insert(self, timestamp, data):
        with self.buf_lock:
            last_ts = self.buf[-1]['timestamp']
            if last_ts < timestamp:
                cnt = (timestamp - last_ts) / self.interval
                self.buf += [
                    {'timestamp': last_ts + i*self.interval, 'data': None}
                    for i in range(1, cnt+1)
                ]
            first_ts = self.buf[0]['timestamp']
            self.buf[(timestamp-first_ts)/self.interval]['data'] = data
        if self.available():
            with self.cv:
                self.cv.notify()

    def available(self):
        for i in range(self.fetch_size):
            if self.buf[self.cur+i]['data'] is not None:
                return True
        return False

    def fetch(self):
        with self.cv:
            self.cv.wait_for(self.available)
            data = self.buf[self.cur]['data']
            if data is None:
                data = self.last_data
            else:
                self.last_data = data
            self.cur = self.cur + 1
            if self.cur > 2*self.fetch_size:
                self.cur -= self.fetch_size
                self.buf = self.buf[self.fetch_size:]
            return data

    def seek(self, offset):
        pass

    def close(self):
        pass