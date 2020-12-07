import asyncio

from client_network import client_network_main
from client_vlc import client_vlc_main
from client_utility import MediaBuffer

async def main():
    msg_queue = asyncio.Queue(1024)

    buffer = MediaBuffer(100, 65536, 4)

    await asyncio.gather(
        client_network_main(msg_queue, buffer),
        client_vlc_main(msg_queue, buffer)
    )

if __name__ == "__main__":

    asyncio.run(main())

    pass