import asyncio
import argparse

from client_network import client_network_main
from client_vlc import createWindow
from client_utility import MediaBuffer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Stream Media Player -- Client')
    parser.add_argument('-ip', default="localhost", type=str)
    parser.add_argument('-port', default=8888, type=int)
    args = parser.parse_args()
    ip = args.ip
    port = args.port
    msg_queue = asyncio.Queue(1024)

    buffer = MediaBuffer(16, 32*1024*1024)

    createWindow(msg_queue, buffer, client_network_main, ip, port)
