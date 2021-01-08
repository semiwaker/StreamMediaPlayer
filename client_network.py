import asyncio
import socket

from client_utility import MediaBuffer

async def client_network_main(msg_queue, buffer):
    # msg_queue: asyncio.Queue()
    # buffer: MediaBuffer
    retry = True
    while retry:
        s = socket.socket()
        host = socket.gethostname()
        port = 23333
    
        local_server = ServerProtocol(loop, buffer)
        client = ClientProtocol(loop, buffer, host, port)

        async def server_main(local_server, loop, buffer):
            await loop.create_server(local_server, host, port)

        v_server_host = '远程服务器hostname'
        v_server_port = 12345

        async def client_main(client, v_host, v_buffer, loop, buffer):
            await loop.create_connection(client, v_server_host, v_server_port)

    
        async def process_msg(msg_queue):
            while True:
                msg = await msg_queue.get()
            # msg = msg.split()
            # if msg[0] == 'list':
            #     client.write_msg('list')
            # elif msg[0] == 'file':
            #     client.write_msg(('file ' + msg[1]))
            # elif msg[0] == 'continue':
            #     client.write_msg('continue')
            # elif msg[0] == 'pause':
            #     client.write_msg(('pause ' + msg[1]))
            # elif msg[0] == 'end':
            #     client.write_msg('end')
            # elif msg[0] == 'seek':
            #     client.write_msg(('seek ' + msg[1]))
            client.write_msg(msg)
        loop = asyncio.get_event_loop()
        tasks=[
            server_main(local_server, loop, buffer), 
            client_main(client, v_server_host, v_server_port, loop, buffer),
            process_msg(msg_queue)
        ]
        loop.run_until_complete(tasks)
        loop.run_forever()




class ClientProtocol(asyncio.Protocol):
    def __init__(self, loop, buffer, l_server_host, l_server_port):
        self.loop = loop
        self.buffer = buffer
        self.transport = None
        self.num_failure = 0
        self.l_server_host = l_server_host
        self.l_server_port = l_server_port
        self.last_msg = {'list' : None, 'file' : None, 'continue' : None, 'pause' : None, 'end' : None, 'seek' : None}

    def connection_made(self, transport):
        self.transport = transport
        transport.write()
        

    def data_received(self, data):
        data_list = data.decode().split()
        data_list[0] = msg
        if data_list[1] == 'No':
            self.num_failure += 1
            if self.num_failure < 3:
                self.write_msg(last_msg[data_list[0]])   # 重发上一条同类信息
            else:
                # ???通知用户服务器拒绝访问
        else:   
            self.num_failure = 0 
            if msg == 'list':
                file_num = int(data_list[1])
                file_list = data_list[2:]
                # ???传回file_num, file_list
            elif msg == 'end':
                self.loop.stop()
                # ???结束

    def connection_lost(self, exc):
        # ???是否要通知
        self.loop.stop()

    def write_msg(msg):
        if msg == None:
            return False
        transport.write(msg.encode())
        msg_list = msg.split()
        self.last_msg[msg_list[0]] = msg
        return True

class ServerProtocol(asyncio.Protocol):
    def __init__(self, loop, buffer):
        self.loop = loop
        self.buffer = buffer
        self.transport = transport

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        # ???数据处理
        self.buffer.insert(data.timestamp, data.data)
        # 如果buffer快满了，通知server
        if(buffer.almost_full()):
            self.transport.write('almost_full'.encode())

    def connection_lost(self, exc):
        # ???是否要通知
        self.loop.stop()
