# ===========================================
# @Time    : 2018/5/18 15:01
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : tcpudp.py
# @Software: PyCharm Community Edition
# ===========================================

# import asyncio
import gevent.monkey
gevent.monkey.patch_all()
from collections import deque
from functools import wraps
import gevent
import socket, sys
import pandas as pd
pd.set_option('display.width', 5000)
pd.option_context('display.precision', 3)
import time
now = lambda: time.time()


# 内部函数使用参数的装饰器
def genel_try_dec(handel_func):
    """handel_func通用异常处理
    """
    @wraps(handel_func)
    def do_func(*args, **kwargs):
        try:
            res = handel_func(*args, **kwargs)
        except Exception as err:
            res = 0
            print('genel try Exception', __name__, err.args)
        return res
    return do_func


# 内部函数使用参数，装饰器也使用参数
def polling_dec(dt=60):
    """通用轮询
    """
    def wrapper(func):
        def _wrapper(*args, **kargs):
            while 1:
                func(*args, **kargs)
                time.sleep(dt)
        return _wrapper
    return wrapper


# Socket Communicate base class
class SoC:

    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dqueue = deque([])  # 消息处理队列

    @staticmethod
    def raise_error(err_mess):
        raise AttributeError(err_mess)

    def close(self, tp=2):
        # 0 SHUT_RD 关闭接收消息通道，1 SHUT_WR 关闭发送消息通道，2 SHUT_RDWR 两个通道都关闭。
        self.soc.shutdown(tp)
        self.soc.close()

    def send_message(self, *args):
        print(args)
        self.raise_error('子类必须实现这个方法:%s' % __name__)

    def recv_handle(self, *args):
        print(args)
        self.raise_error('子类必须实现这个方法:%s' % __name__)

    def listen_bytimes(self, times=None, handle_func=None):
        if handle_func is None:
            handle_func = self.mess_tudeque
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
    def mess_tudeque(self, mess, addr, soc_object=None):
        # soc_object = soc_object if soc_object else self.soc  # 最好去掉这种默认
        try:
            mess_ = mess.decode()
            messcode, messbody = self.mess_protocol(mess_)
            self.dqueue.append((messcode, messbody, addr, soc_object))
        except Exception as err:
            print('mess_tudeque_error', str(err))

    def process_dque(self):
        if len(self.dqueue):
            mess_head, mess_body, addr, soc_object = self.dqueue.popleft()
            print('Processing :: self.handle', mess_head, mess_body, addr, soc_object)
            try:
                eval('self.handle%s' % mess_head)(mess_body, addr, soc_object)
            except Exception as err:
                print('processing eval error !!', err, err.args, mess_head)
            # eval('self.handle%s' % mess_head)(mess_body, addr, soc_object)
        else:
            gevent.sleep(.5)
            # print('dqueue clean', len(self.dqueue), len(self.dqueue), end='\r')

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

    def __init__(self, l_addr=None, timeout=None):
        super(UdpSocket, self).__init__()
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if l_addr:
            self.soc.bind(l_addr)
        if timeout:
            self.soc.settimeout(timeout)
        # self.handle_func = self.listen_todeque  # set_default_handlefunc

    def send_message(self, message, addr, soc_object=None):
        # print('send UDP message( %s ) ===>> ' % message, addr)
        soc_object = soc_object if soc_object else self.soc
        soc_object.sendto(message.encode(), addr)

    def recv_handle(self, handle_func, with_spawn=True):
        try:
            mess, addr = self.soc.recvfrom(65507, )
            if with_spawn:
                return gevent.spawn(handle_func, mess, addr, )
            else:
                return handle_func(mess, addr, )
        except Exception as err:
            print(err)


class TcpSocket(SoC):

    def __init__(self, l_addr=None, ):
        super(TcpSocket, self).__init__()
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.binded_speaker = None
        if l_addr:
            self.soc.bind(l_addr)

    def send_message(self, message, addr, soc_object=None):  #
        print('send TCP message( %s ) ===>> ' % message, addr, soc_object, )
        if soc_object:
            if soc_object.getpeername() == addr:
                soc_object.send(message.encode())
                return soc_object
            else:
                print('soc_object is to ', soc_object.getpeername(), 'but addr is', addr)
        else:
            # try:
            self.soc.connect(addr)
            self.soc.send(message.encode())
            return self.soc
            # except Exception as err:
            #     print('self send_message error', err)
            #     self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #     self.soc.bind(self.l_addr)
            #     self.soc.connect(addr)
            #     self.soc.send(message.encode())
            #     return self.soc

    def recv_handle(self, handle_func, with_spawn=True):
        try:
            self.soc.listen(1000)  # TCP的最大连接数
            sock, addr = self.soc.accept()
            print('Welcome', sock, addr, sock.getpeername())
            mess = sock.recv(1024, )
            if with_spawn:
                gevent.spawn(handle_func, mess, addr, sock)
            else:
                handle_func(mess, addr, sock)
        except Exception as err:
            print(err)

    def re_bind(self, l_addr=None):
        l_addr = l_addr if l_addr else self.soc.getsockname()
        print(id(self.soc), self.soc)
        self.close()
        print(id(self.soc), self.soc)
        self.__init__(l_addr)
        print(id(self.soc), self.soc)


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