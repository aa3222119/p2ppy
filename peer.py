# ===========================================
# @Time    : 2018/5/21 15:23
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : peer.py
# @Software: PyCharm Community Edition
# ===========================================

# from hashlib_func import *
from protocol_ import *
from tcpudp import *
import time, sys, threading
now = lambda: time.time()

# class UdpPeer(UdpSocket):


# 生成自己的address, 应通过加密模块获取,  模拟先取 sys.argv[1]

host_loop = getip_(0)[0]
if len(sys.argv) < 2:
    sys.argv.append(' beta antony')
mess_basedict = {'address': host_loop + str(sys.argv[1])}

# 知识节点
imformater_list = [('47.104.190.254', 10036), ('120.77.65.191', 10036), ('120.25.245.164', 10036)]

print('host_loop', host_loop)
laddr = (host_loop, 10036)
laddr_sender = (host_loop, 10038)

mess_di = mess_basedict.copy()
mess_di['laddr'] = laddr
mess_di['timestamp'] = now()

main_imformater = imformater_list.pop(0)
sub_imformater = imformater_list.pop(0)


class UdpPeer(UdpSocket):

    @genel_try_dec
    def handle1002(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no1)
        self.send_message(str(routein_no2) + str(mess_di), addr, soc_object)

    @genel_try_dec
    def handle1003(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no2)
        addr = (main_imformater[0], main_imformater[1]+1)
        self.send_message(str(routein_no3) + str(mess_di), addr, soc_object)

    @genel_try_dec
    def handle1004(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no3)
        mess_di['oaddr'] = (main_imformater[0], main_imformater[1] + 1)
        addr = sub_imformater
        self.send_message(str(routetransfer_no4) + str(mess_di), addr, soc_object)

    def handle1005(self, *args):
        print('1005', *args, self)

    def handle1006(self, *args):
        print('1006', *args, self)


class TcpPeer(TcpSocket):

    def send_message(self, message, addr, soc_object=None):
        soc_object = super(TcpPeer,self).send_message(message, addr, soc_object=None)
        data = soc_object.recv(1024, )
        soc_object.shutdown(2)
        soc_object.close()
        gevent.sleep(.5)
        print('data', data)
        self.mess_tudeque(data, addr, )

    def handle1002(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no1)
        self.send_message(str(routein_no2) + str(mess_di), addr, soc_object)


    def handle1003(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no2)
        addr = (main_imformater[0], main_imformater[1] + 1)
        self.send_message(str(routein_no3) + str(mess_di), addr, soc_object)

    def handle1004(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no3)
        mess_di['oaddr'] = (main_imformater[0], main_imformater[1] + 1)
        addr = sub_imformater
        self.send_message(str(routetransfer_no4) + str(mess_di), addr, soc_object)

    def handle1005(self, *args):
        print('1005', *args, self)

    def handle1006(self, *args):
        print('1006', *args, self)


udp36 = UdpPeer(laddr, )
tcp36 = TcpPeer(laddr, )
tcp36_listener = TcpPeer(laddr, )

if __name__ == "__main__":
    threading.Thread(target=udp36.listen_bytimes, args=(100, )).start()
    threading.Thread(target=udp36.loop_process, args=()).start()
    udp36.send_message(str(routein_no1) + str(mess_di), main_imformater)
    # threading.Thread(target=tcp36_listener.listen_bytimes, args=(100,)).start()
    threading.Thread(target=tcp36.loop_process, args=()).start()
    tcp36.send_message(str(routein_no1) + str(mess_di), main_imformater)


