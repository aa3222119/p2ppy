# ===========================================
# @Time    : 2018/5/18 15:01
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : tcpudp.py
# @Software: PyCharm Community Edition
# ===========================================

# import asyncio
from collections import deque
import gevent
import socket
from gevent import socket, monkey, server
monkey.patch_all()


class UdpSocket():
    def __init__(self, l_addr, timeout=None):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.bind(l_addr)
        if timeout:
            self.soc.settimeout(timeout)
        self.dqueue = deque([])  # 消息处理队列
        # self.handle_func = self.listen_todeque  # set_default_handlefunc
        self.process_map = {}

    def send_message(self, message, addr):
        print('send message(%s) ===>> ' % message, addr)
        self.soc.sendto(message.encode(), addr)

    def recv_handle(self, handle_func, with_spawn=True):
        try:
            mess, addr = self.soc.recvfrom(1024, )
            if with_spawn:
                gevent.spawn(handle_func, mess, addr)
            else:
                handle_func(mess, addr)
        except Exception as err:
            print(err)
        return 0

    # @asyncio.coroutine
    def listen_bytimes(self, times=None, handle_func=None):
        if handle_func is None:
            handle_func = self.listen_todque
        print('listening ...', self.soc.getsockname(), times, 'times')
        if times is None:
            while True:
                self.recv_handle(handle_func)
        else:
            for i in range(times):
                self.recv_handle(handle_func)

    # 是否满足设计的消息协议,能预处理后放入待处理队列
    def listen_todque(self, mess, addr):
        try:
            mess_ = mess.decode()
            messcode, messbody = int(mess_[:4]), mess_[4:]  # 后期可以设计为消息协议
            self.dqueue.append((messcode, messbody, addr))
        except Exception as err:
            print('listen_todque_error', str(err))

    @staticmethod
    def just_return(**kwargs):
        return kwargs


# def udp_handle_func(soc, mess_addr):
#     mess, addr = mess_addr
#     print(soc, mess_addr)
#     time.sleep(1)
#     mess = 'got this %s %s' %addr
#     print('finash send!!')
#     soc.sendto(mess.encode(), addr)


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


def getip_(is_local=True):
    """
    获取本机内/外网ip
    """
    import socket
    try:
        if is_local:
            addr = socket.gethostbyname_ex(socket.gethostname())
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            addr = s.getsockname()
            s.close()
        return addr
    except Exception as err:
        print(err)
        return 0
