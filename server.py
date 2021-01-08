import asyncio
import file_transfer
import os


async def server_main():
    await asyncio.start_server(response, "127.0.0.1", 8888)


async def response(reader, writer):
    while True:
        msg = await reader.readline()
        # TODO:
        blocks = msg.split(' ')
        a = blocks[0]
    if(a == 'list'):
        message = os.listdir('.')
    elif(a == 'file'):
        cap = cv2.VideoCapture(quest[1])
        if cap.isOpened():
            frames_num = cap.get(7)
            message = ['ok', frames_num]
            transfer_video(cap)
        else:
            message = 'no'
    elif(a == 'continue')
    return 'ok'
    elif(a == 'pause')
    t = quest[1]
    return 'ok'
    elif(a == 'end')
    return 'ok'
    elif(a == 'seek')
    t = quest[1]
    return 'ok'

if __name__ == "__main__":
    asyncio.run(server_main())
