import asyncio

from client_network import client_network_main
from client_vlc import createWindow
from client_utility import MediaBuffer


if __name__ == "__main__":
    msg_queue = asyncio.Queue(1024)

    buffer = MediaBuffer(32, 32*1024*1024)

    createWindow(msg_queue, buffer, client_network_main)
