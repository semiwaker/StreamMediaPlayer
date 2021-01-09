import asyncio
import socket
import struct

# from client_utility import MediaBuffer


async def client_network_main(msg_queue, buffer):
    print("client_network_main")
    # msg_queue: asyncio.Queue()
    # buffer: MediaBuffer

    # num_failure = 0
    # self.last_msg = {'list': None, 'file': None,
    # 'continue': None, 'pause': None, 'end': None, 'seek': None}

    # s = socket.socket()

    host = socket.gethostname()
    port = 23333
    buffer.set_host_port(host, port)

    # local_server = ServerProtocol(loop, buffer)
    # client = ClientProtocol(loop, buffer, host, port)

    # async def server_main(local_server, loop, buffer):
    #     await loop.create_server(local_server, host, port)

    v_server_host = '127.0.0.1'
    v_server_port = 8888

    v_reader, v_writer = await asyncio.open_connection(
        v_server_host,
        v_server_port
    )
    print("Connected")
    buffer.set_writer(v_writer)
    buffer.set_reader(v_reader)

    async def check_continue(reader, writer):
        while buffer.reading:
            if buffer.paused and len(buffer.buf) <= 0.8 * buffer.max_size:
                async with buffer.wr_lock:
                    v_writer.write(b'continue\n')
                    await v_writer.drain()
                    await v_reader.readline()
            else:
                await asyncio.sleep(1)

    async def response(reader, writer):
        asyncio.create_task(check_continue(reader, writer))
        while buffer.reading:
            data = await reader.readexactly(8)
            length, seq = struct.unpack("2i", data)
            print("Recived", seq, length)
            fdata = await reader.readexactly(length)
            buffer.insert(seq, fdata)
            # 如果buffer快满了，通知server
            writer.write(bytes(str(seq) + '\n', encoding='utf-8'))
            await writer.drain()
            if len(buffer.buf) > 0.8 * buffer.max_size:
                buffer.paused = True
                async with buffer.wr_lock:
                    v_writer.write(b'pause\n')
                    await v_writer.drain()
                    await v_reader.readline()

    asyncio.create_task(asyncio.start_server(response, host, port))

    while True:
        await buffer.playing.wait()
        msg = await msg_queue.get()
        # print("Msg:", msg)
        # if msg['type'] == 'play':
        #     v_writer.write(b'continue\n')
        #     await v_writer.drain()
        #     await v_reader.readline()
        # elif msg['type'] == 'pause':
        #     v_writer.write(b'pause\n')
        #     await v_writer.drain()
        #     await v_reader.readline()
        if msg['type'] == 'stop':
            print("Stop")
            buffer.reading = False
            async with buffer.wr_lock:
                v_writer.write(b'end\n')
                await v_writer.drain()
                await v_reader.readline()
        # elif msg['type'] == 'seek':
            # v_writer.write(bytes('seek ' + msg[1] + '\n', encoding='utf-8'))
