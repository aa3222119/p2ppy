# ===========================================
# @Time    : 2018/5/18 15:01
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : tcpudp.py
# @Software: PyCharm Community Edition
# ===========================================

# import asyncio
from collections import deque
from functools import wraps
import gevent
import socket
from gevent import socket, monkey, server
monkey.patch_all()


def genel_try_dec(handel_func):
    @wraps(handel_func)
    def do_func(*args, **kwargs):
        try:
            res = handel_func(*args, **kwargs)
        except Exception as err:
            res = 0
            print('genel try Exception', __name__, err.args)
        return res
    return do_func


# Socket Communicate base class
class SoC:

    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dqueue = deque([])  # 消息处理队列

    @staticmethod
    def raise_error(err_mess):
        raise AttributeError(err_mess)

    def conn(self, *args):
        print(args)

    def close(self):
        # 0 SHUT_RD 关闭接收消息通道，1 SHUT_WR 关闭发送消息通道，2 SHUT_RDWR 两个通道都关闭。
        self.soc.shutdown(1)
        self.soc.close()

    def send_message(self, *args):
        print(args)
        self.raise_error('子类必须实现这个方法:%s' % __name__)

    def recv_handle(self, *args):
        print(args)
        self.raise_error('子类必须实现这个方法:%s' % __name__)

    def listen_bytimes(self, times=None, handle_func=None):
        if handle_func is None:
            handle_func = self.listen_todque
        print('listening ...%s; type:%s; %s times' % (self.soc.getsockname(), self.soc.type, times))
        if times is None:
            while True:
                self.recv_handle(handle_func)
        else:
            for i in range(times):
                self.recv_handle(handle_func)

    @staticmethod         # 设计为消息协议
    def mess_protocol(mess):
        return int(mess[:4]), mess[4:]

    # 是否满足设计的消息协议,能预处理后放入待处理队列
    def listen_todque(self, mess, addr, soc_object=None):
        soc_object = soc_object if soc_object else self.soc
        try:
            mess_ = mess.decode()
            messcode, messbody = self.mess_protocol(mess_)
            print('dqueue.append', messcode, messbody, addr, soc_object.getsockname())
            self.dqueue.append((messcode, messbody, addr, soc_object))

        except Exception as err:
            print('listen_todque_error', str(err))

    def process_dque(self):
        if len(self.dqueue):
            mess_head, mess_body, addr, soc_object = self.dqueue.popleft()
            try:
                print(mess_body, addr)
                eval('self.handle%s' % mess_head)(mess_body, addr, soc_object)
            except Exception as err:
                print(err, mess_head)
        else:
            gevent.sleep(.5)
            print('dqueue clean', len(self.dqueue), len(self.dqueue), end='\r')

    def loop_process(self, times=None):
        if times is None:
            while True:
                self.process_dque()
        else:
            for i in range(times):
                self.process_dque()

    def for_test_id(self):
        print(__name__, 'for_test_id', id(self))


class UdpSocket(SoC):

    def __init__(self, l_addr, timeout=None):
        super(UdpSocket, self).__init__()
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind(l_addr)
        if timeout:
            self.soc.settimeout(timeout)
        # self.handle_func = self.listen_todeque  # set_default_handlefunc

    def send_message(self, message, addr, soc_object=None):
        print('send message(%s) ===>> ' % message, addr)
        soc_object = soc_object if soc_object else self.soc
        soc_object.sendto(message.encode(), addr)

    def recv_handle(self, handle_func, with_spawn=True):
        try:
            mess, addr = self.soc.recvfrom(1024, )
            if with_spawn:
                gevent.spawn(handle_func, mess, addr, )
            else:
                handle_func(mess, addr, )
        except Exception as err:
            print(err)


class TcpSocket(SoC):

    def __init__(self, l_addr, handle_func=print):
        super(TcpSocket, self).__init__()
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind(l_addr)
        self.soc_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc_listen.bind(l_addr)

    def conn(self, addr):
        self.soc.connect(addr)

    def send_message(self, message, addr, soc_object=None):
        print('send message(%s) ===>> ' % message, addr)
        if soc_object and soc_object.getsockname() == addr:
            soc_object.send(message.encode())
        else:
            self.soc.connect(addr)
            self.soc.send(message.encode())

    def recv_handle(self, handle_func, with_spawn=True):
        try:
            self.soc_listen.listen(1000)  # TCP的最大连接数
            sock, addr = self.soc_listen.accept()
            print('Welcome', sock, addr, sock.getpeername())
            mess = sock.recv(1024, )
            if with_spawn:
                gevent.spawn(handle_func, mess, addr, sock)
            else:
                handle_func(mess, addr, sock)
        except Exception as err:
            print(err)


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
