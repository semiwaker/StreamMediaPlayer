import asyncio
import os
import struct
# import random


async def server_main():
    await asyncio.start_server(response, "127.0.0.1", 8888)


async def response(reader, writer):
    is_playing = True
    ended = False

    while True:
        msg = await reader.readline()
        blocks = msg.split(' ')
        a = blocks[0]
        if a == b'list':
            message = os.listdir('./media')
            writer.writelines([message])
            await writer.drain()
        elif a == b'file':
            ok = True
            try:
                os.chdir(['./media/', blocks[1]])
            except OSError:
                writer.writelines([b'no'])
                await writer.drain()
                ok = False
            if ok:
                videolist = os.listdir()
                length = len(videolist)
                # rand = random.randint(1,2**31-1)
                writer.writelines([bytes('ok '+str(length), encoding="utf-8")])
                await writer.drain()
                is_playing = True
                reader2, writer2 = await asyncio.open_connection(blocks[2], int(blocks[3]))
                asyncio.create_task(file_transfer(
                    videolist, reader2, writer2, is_playing, ended))

        elif a == b'continue':
            is_playing = True
            writer.writelines([b'ok'])
            await writer.drain()
        elif a == b'pause':
            is_playing = False
            writer.writelines([b'ok'])
            await writer.drain()
        elif a == b'end':
            ended = True
            writer.writelines([b'ok'])
            await writer.drain()


async def file_transfer(videolist, reader2, writer2, is_playing, ended):
    ptr = 0
    while not ended:
        if is_playing:
            with open(videolist[ptr], 'rb') as videofile:
                data = videofile.read()
                d = struct.pack("2i", len(data), ptr)
                writer2.write(d+data)
                await writer2.drain()
            ptr += 1
            if(ptr >= len(videolist)):
                ended = 1
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(server_main())
