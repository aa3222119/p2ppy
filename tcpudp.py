# ===========================================
# @Time    : 2018/5/18 15:01
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : tcpudp.py
# @Software: PyCharm Community Edition
# ===========================================

import asyncio
import gevent
import socket
from gevent import socket, monkey, server
# monkey.patch_all()

class UdpSocket():
    def __init__(self, l_addr, timeout=None):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.bind(l_addr)
        if timeout:
            self.soc.settimeout(timeout)

    def send_message(self, message, addr):
        self.soc.sendto(message.encode(), addr)

    def recv_handle(self, hadle_func=print):
        try:
            hadle_func(self.soc, self.soc.recvfrom(1024,))
        except Exception as err:
            print(err)

    def listen_bytimes(self, times):
        for i in range(times):
            self.recv_handle(udp_handle_func)


def udp_handle_func(soc, mess_addr):
    mess, addr = mess_addr
    mess = 'got this %s %s' %addr
    soc.sendto(mess.encode(), addr)


class TcpSocket():

    def __init__(self, l_addr=None, handle_func=print):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if l_addr:
            if handle_func:
                self.server = server.StreamServer(l_addr, handle_func)
            else:
                self.soc.bind(l_addr)

    def conn(self, addr):
        self.soc.connect(addr)

    def send_message(self, message):
        self.soc.send(message.encode())

    def recv_handle(self, hadle_func=print):
        try:
            hadle_func(self.soc.recv(1024,))
        except Exception as err:
            print(err)


def server_handle_func(soc, address):
    data = soc.recv(1024)
    print(data, address)
    soc.send("Hello clinet!\n %".encode())
    return soc


# playground
