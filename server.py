import argparse
import asyncio
import os
import struct
# import random


async def server_main(ip, port):
    await asyncio.start_server(response, ip, port)
    print("Start server")
    while True:
        await asyncio.sleep(1)


async def response(reader, writer):
    print("Connected")
    status = {
        "is_playing": True,
        "ended": False
    }

    while not writer.is_closing():
        msg = await reader.readline()
        if msg == b'':
            break
        blocks = msg.strip().split()
        print(blocks)
        a = blocks[0]
        if a == b'list':
            names = os.listdir('./media')
            message = ([bytes(str(len(names))+'\n', encoding='utf-8')] +
                       [bytes(i+'\n', encoding='utf-8') for i in names])
            print(message)
            writer.writelines(message)
            await writer.drain()
        elif a == b'file':
            p = f'./media/{str(blocks[1], encoding="utf-8")}'
            if not os.path.exists(p):
                writer.write(b'no\n')
                await writer.drain()
                continue
            videolist = os.listdir(p)
            print(videolist)
            length = len(videolist)
            # rand = random.randint(1,2**31-1)
            writer.write(bytes('ok '+str(length)+'\n', encoding="utf-8"))
            await writer.drain()
            status["is_playing"] = True
            status["ended"] = False
            reader2, writer2 = await asyncio.open_connection(
                blocks[2],
                int(blocks[3])
            )
            print("Video server-client connected")
            asyncio.create_task(file_transfer(
                p, videolist, reader2, writer2, status))

        elif a == b'continue':
            status["is_playing"] = True
            writer.write(b'ok\n')
            await writer.drain()
        elif a == b'pause':
            status["is_playing"] = False
            writer.write(b'ok\n')
            await writer.drain()
        elif a == b'end':
            status["ended"] = True
            writer.write(b'ok\n')
            await writer.drain()
        print("Replied")


async def file_transfer(p, videolist, reader2, writer2, status):
    ptr = 0
    while not status["ended"]:
        if status["is_playing"]:
            with open(os.path.join(p, f"{ptr}.ts"), 'rb') as videofile:
                data = videofile.read()
            d = struct.pack("2i", len(data), ptr)
            print("Send", f"{ptr}.ts", ptr, len(data))
            writer2.write(d+data)
            await writer2.drain()
            ack = await reader2.readline()
            print("Ack", ack)
            ptr += 1
            if(ptr >= len(videolist)):
                status["ended"] = 1
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Stream Media Player -- Server')
    parser.add_argument('-ip', default="localhost", type=str)
    parser.add_argument('-port', default=8888, type=int)
    args = parser.parse_args()
    ip = args.ip
    port = args.port
    msg_queue = asyncio.Queue(1024)

    asyncio.run(server_main(ip, port))
