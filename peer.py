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
import time, sys
now = lambda: time.time()

# class UdpPeer(UdpSocket):


# 生成自己的address, 应通过加密模块获取,  模拟先取 sys.argv[1]

host_loop = getip_(0)[0]
if len(sys.argv) < 2:
    sys.argv.append(' beta antony')
mess_basedict = {'address': host_loop + str(sys.argv[1])}

# 知识节点
imformater_list = [('47.104.190.254', 10036), ('120.77.65.191', 10036), ('120.25.245.164', 10036)]


laddr = (host_loop, 10036)
udp36 = UdpSocket(laddr, 4)

mess_di = mess_basedict.copy()
mess_di['laddr'] = laddr
mess_di['timestamp'] = now()

main_imformater = imformater_list.pop(0)
sub_imformater = imformater_list.pop(0)

udp36.send_message(str(routein_no1)+str(mess_di), main_imformater)
mess, addr = udp36.soc.recvfrom(1024,)
mess = mess.decode()
if mess[:4] == str(routein_no2):
    mess_di['last_process_key'] = (mess_di['address'], routein_no1)
    udp36.send_message(str(routein_no2) + str(mess_di), main_imformater)
    mess, addr = udp36.soc.recvfrom(1024, )
    mess = mess.decode()
    if mess[:4] == str(routein_no3):
        mess_di['last_process_key'] = (mess_di['address'], routein_no2)
        udp36.send_message(str(routein_no3) + str(mess_di), (main_imformater[0], main_imformater[1]+1))
        mess, addr = udp36.soc.recvfrom(1024, )
        mess = mess.decode()
        if mess[:4] == str(routein_no4):
            mess_di['last_process_key'] = (mess_di['address'], routein_no3)
            mess_di['oaddr'] = (main_imformater[0], main_imformater[1]+1)
            udp36.send_message(str(routetransfer_no4) + str(mess_di), sub_imformater)
            print(udp36.soc.recvfrom(1024, ))
        else:
            print(mess, addr)
    else:
        print(mess, addr)
else:
    print(mess, addr)


class Peer():

    def __init__(self):
        pass