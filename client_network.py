import asyncio
import socket
import struct

from client_utility import MediaBuffer


async def client_network_main(msg_queue, buffer):
    # msg_queue: asyncio.Queue()
    # buffer: MediaBuffer

    num_failure = 0
    self.last_msg = {'list': None, 'file': None,
        'continue': None, 'pause': None, 'end': None, 'seek': None}

    s = socket.socket()
    host = socket.gethostname()
    port = 23333

        # local_server = ServerProtocol(loop, buffer)
        # client = ClientProtocol(loop, buffer, host, port)

        # async def server_main(local_server, loop, buffer):
        #     await loop.create_server(local_server, host, port)
    async def response(reader, writer):
        while True:
            data = reader.read()
            data = struct.unpack(data.decode())
            self.buffer.insert(data[0], data[1])
            # 如果buffer快满了，通知server
            writer.write(data[1].encode())
            if(len(buffer.buf) > 0.8 * buffer.max_size):
                writer.write('pause'.encode())

    await asyncio.start_server(response, host, port)

    v_server_host = '远程服务器hostname'
    v_server_port = 12345

    v_reader, v_writer = await asyncio.open_connection(v_server_host, v_server_port)
    buffer.set_writer(v_writer)
    burrer.set_reader(v_reader)
    v_writer.write('%s  %d' % (host, port).encode())
    # process msg
    while True:
        msg = await msg_queue.get()
        write_msg(msg)

    # async def process_server_msg():
    #     msg = await v_reader.readline()
    #     data_list = data.decode().split()
    #     data_list[0] = msg
    #     if data_list[1] == 'No':
    #         num_failure += 1
    #         if num_failure < 3:
    #             write_msg(last_msg[data_list[0]])   # 重发上一条同类信息
    #         else:
    #             # ???通知用户服务器拒绝访问
    #     else:
    #         num_failure = 0
    #         if msg == 'list':
    #             file_num = int(data_list[1])
    #             file_list = data_list[2:]
    #             # ???传回file_num, file_list
    #         if msg == 'end':
    #             # ???结束

    async def write_msg(msg):
        if msg['type'] == 'list':
            v_writer.write('list')
        elif msg['type'] == 'file':
            v_writer.write(('file ' + msg['filename']))
        elif msg['type'] == 'continue':
            v_writer.write('continue')
        elif msg['type'] == 'pause':
            v_writer.write(('pause')
        elif msg['type'] == 'end':
            v_writer.write('end')
        elif msg['type'] == 'seek':
            v_writer.write(('seek ' + msg[1]))
        last_msg[msg['type']] = msg
        await readline()

    




# class ClientProtocol(asyncio.Protocol):
#     def __init__(self, loop, buffer, l_server_host, l_server_port):
#         self.loop = loop
#         self.buffer = buffer
#         self.transport = None
#         self.num_failure = 0
#         self.l_server_host = l_server_host
#         self.l_server_port = l_server_port
#         self.last_msg = {'list' : None, 'file' : None, 'continue' : None, 'pause' : None, 'end' : None, 'seek' : None}

#     def connection_made(self, transport):
#         self.transport = transport
#         transport.write()


#     def data_received(self, data):
#         data_list = data.decode().split()
#         data_list[0] = msg
#         if data_list[1] == 'No':
#             self.num_failure += 1
#             if self.num_failure < 3:
#                 self.write_msg(last_msg[data_list[0]])   # 重发上一条同类信息
#             else:
#                 # ???通知用户服务器拒绝访问
#         else:
#             self.num_failure = 0
#             if msg == 'list':
#                 file_num = int(data_list[1])
#                 file_list = data_list[2:]
#                 # ???传回file_num, file_list
#             elif msg == 'end':
#                 self.loop.stop()
#                 # ???结束

#     def connection_lost(self, exc):
#         # ???是否要通知
#         self.loop.stop()

#     def write_msg(msg):
#         if msg == None:
#             return False
#         transport.write(msg.encode())
#         msg_list = msg.split()
#         self.last_msg[msg_list[0]] = msg
#         return True

# class ServerProtocol(asyncio.Protocol):
#     def __init__(self, loop, buffer):
#         self.loop = loop
#         self.buffer = buffer
#         self.transport = transport

#     def connection_made(self, transport):
#         peername = transport.get_extra_info('peername')
#         print('Connection from {}'.format(peername))
#         self.transport = transport

#     def data_received(self, data):
#         # ???数据处理
#         self.buffer.insert(data.timestamp, data.data)
#         # 如果buffer快满了，通知server
#         if(len(buffer.buf) > 0.8 * buffer.max_size):
#             self.transport.write('pause'.encode())

#     def connection_lost(self, exc):
#         # ???是否要通知
#         self.loop.stop()
