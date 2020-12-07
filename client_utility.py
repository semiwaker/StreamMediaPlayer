import asyncio


class MediaBuffer:
    def __init__(self, interval, max_size, fetch_size):
        self.buf = [{'timestamp': 0, 'data': None}]
        self.cur = 1
        self.max_size = max_size
        self.interval = interval
        self.fetch_size = fetch_size

    def insert(self, timestamp, data):
        last_ts = self.buf[-1]['timestamp']
        if last_ts < timestamp:
            cnt = (timestamp - last_ts) / interval
            self.buf += [{'timestamp': last_ts + i*interval, 'data': None}
                         for i in range(1, cnt+1)]
        first_ts = self.buf[0]['timestamp']
        self.buf[(timestamp-first_ts)/interval]['data'] = data

    def fetch(self):
        pass
