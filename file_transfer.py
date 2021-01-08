import asyncio

import os
global openfile
global filelength
async def transfer_video(cap):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    while(1):
        frames = [i for i in range(16)]
        isend = 0
        for i in [1,5,9,13,2,6,10,14,3,7,11,15,4,8,12,16]:
            ret, frame = cap.read()
            if ret == false:  
                isend = 1
                writer.write('end')
                await writer.drain()
                break
            frames[i] = frame
            
        if isend == 1:
            break
        writer.write('frames')
        await writer.drain()
    