import asyncio
import file_transfer
import os
global openfile
global filelength
async def response(quest):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    a = quest[0]
    if(a == 'list'):       
        message = os.listdir('.')
    elif(a == 'file'):
        cap = cv2.VideoCapture(quest[1])
        if cap.isOpened():
            frames_num=cap.get(7)
            message = ['ok',frames_num]
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