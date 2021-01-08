import asyncio
import os
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
        if a == 'list':
            message = os.listdir('./media')
            writer.writelines([message])
            await writer.drain()
        elif a == 'file':
            ok = True
            try:
                os.chdir(['./media/', blocks[1]])
            except OSError:
                writer.writelines('no')
                await writer.drain()
                ok = False
            if ok:
                videolist = os.listdir()
                length = len(videolist)
                #rand = random.randint(1,2**31-1)
                writer.writelines(['ok', length])
                await writer.drain()
                is_playing = True
                reader2, writer2 = await asyncio.open_connection(blocks[2], int(blocks[3]))
                asyncio.create_task(file_transfer(
                    videolist, reader2, writer2, is_playing, ended))

        elif a == 'continue':
            is_playing = True
            writer.writelines(['ok'])
            await writer.drain()
        elif a == 'pause':
            is_playing = False
            writer.writelines(['ok'])
            await writer.drain()
        elif a == 'end':
            ended = True
            writer.writelines(['ok'])
            await writer.drain()


async def file_transfer(videolist, reader2, writer2, is_playing, ended):
    ptr = 0
    while not ended:
        if is_playing:
            videofile = open(videolist[ptr])
            writer2.write(videofile)
            ptr += 1
            if(ptr >= len(videolist)):
                ended = 1
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(server_main())
