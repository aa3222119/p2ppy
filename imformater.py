# ===========================================
# @Time    : 2018/5/18 17:12
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : imformater.py
# @Software: PyCharm Community Edition
# ===========================================

import time, threading
now = lambda: time.time()
import pandas as pd
# from hashlib_func import *
from tcpudp import *
from protocol_ import *

listen_mainport = 10036
listen_sport = 10037
local_loop = '0.0.0.0'
imformaters_di = {}
# route_df = pd.DataFrame({'host': '0.0.0.0', 'port': listen_sport, 'phost': '0.0.0.0', 'pport': listen_sport,
#                          'NAT': -1, 'update_time': now(), 'verify_taken': 0, 'p2p_times': 0,
#                          }, index=[str('1')],
#                         columns=['host', 'port', 'phost', 'pport', 'NAT', 'update_time', 'verify_taken', 'p2p_times'])
route_df = pd.DataFrame({}, columns=['host', 'port', 'phost', 'pport', 'NAT',
                                     'update_time', 'verify_taken', 'p2p_times'])
need_list = ['laddr', 'address', 'timestamp']
need_list23 = need_list + ['last_process_key']
need_list4 = need_list23 + ['paddr']


class UdpImformater(UdpSocket):
    
    route_df = pd.DataFrame({}, columns=['host', 'port', 'phost', 'pport', 'NAT',
                                         'update_time', 'verify_taken', 'p2p_times'])
    processing_nat = {}  # 进行中的端口映射对 (网络标示,消息):先前一致的端口映射  先前一致的端口映射peer也可以存下来验证


class TcpImformater(TcpSocket):

    route_df = pd.DataFrame({}, columns=['host', 'port', 'phost', 'pport', 'NAT',
                                         'update_time', 'verify_taken', 'p2p_times'])
    processing_nat = {}  # 进行中的端口映射对 (网络标示,消息):先前一致的端口映射  先前一致的端口映射peer也可以存下来验证


def fix_route(self, mess, NAT, addr):
    update_time = now()
    verify_taken = update_time - mess['timestamp']
    p2p_times = 0
    if mess['address'] in self.route_df.index:
        p2p_times = self.route_df.loc[mess['address'], 'p2p_times']
        self.route_df.drop(mess['address'], inplace=True)
    self.route_df.loc[mess['address']] = {'host': mess['laddr'][0], 'port': mess['laddr'][1],
                                          'phost': addr[0], 'pport': addr[1], 'update_time': now(),
                                          'verify_taken': verify_taken, 'NAT': NAT, 'p2p_times': p2p_times}



def handle1001(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list]):
        if mess['laddr'] == addr:
            self.fix_route(mess, 0, addr)
            mess_response = str(routein_finish)
        else:
            self.processing_nat.update({(mess['address'], routein_no1): (mess['laddr'], addr)})
            mess_response = str(routein_no2)
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle1002(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list23]):
        if mess['last_process_key'] not in self.processing_nat:
            mess_response = str(routein_no1)
        else:
            last_process_value = self.processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], addr):
                self.processing_nat.update({(mess['address'], routein_no2): last_process_value})
                mess_response = str(routein_no3)
            else:
                self.fix_route(mess, 4, addr)
                mess_response = str(routein_finish)
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle1003(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list23]):
        if mess['last_process_key'] not in self.processing_nat:
            mess_response = str(routein_no1)
        else:
            last_process_value = self.processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], addr):
                self.processing_nat.update({(mess['address'], routein_no3): last_process_value})
                mess_response = str(routein_no4)
            else:
                self.fix_route(mess, 3, addr)
                mess_response = str(routein_finish)
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle1004(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list4]):
        imformaters_di[addr] = None   # 由于1004消息一定来自于其他imforma转发
        if mess['last_process_key'] not in self.processing_nat:
            mess_response = str(routein_no1)
        else:
            last_process_value = self.processing_nat.pop(mess['last_process_key'])
            nattype = 1 if last_process_value == (mess['laddr'], mess['paddr']) else 2
            self.fix_route(mess, nattype, last_process_value[1])
            # last_process_value[1] 存储的是1003时的paddr
            mess_response, addr = str(routein_finish), last_process_value[1]
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle3004(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list + ['oaddr']]):
        mess['paddr'] = addr
        addr = mess.pop('oaddr')
        mess_response = str(routein_no4) + str(mess)
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


UdpImformater.fix_route = fix_route
UdpImformater.handle1001 = handle1001
UdpImformater.handle1002 = handle1002
UdpImformater.handle1003 = handle1003
UdpImformater.handle1004 = handle1004
UdpImformater.handle3004 = handle3004

TcpImformater.fix_route = fix_route
TcpImformater.handle1001 = handle1001
TcpImformater.handle1002 = handle1002
TcpImformater.handle1003 = handle1003
TcpImformater.handle1004 = handle1004
TcpImformater.handle3004 = handle3004


def show_status(imformater):
    print('**********show_status**********  ',imformater,'.processing_nat', imformater.processing_nat, end='\n')
    route_df_show = imformater.route_df.copy()
    route_df_show['dt_'] = now() - route_df_show['update_time']
    print(route_df_show, end='\n')

# -------------------------------------------------------------playground-------------------------------------------------------------
start = now()

udp36 = UdpImformater((local_loop, listen_mainport))
udp37 = UdpImformater((local_loop, listen_sport))
threading.Thread(target=udp36.listen_bytimes, args=(100,)).start()
threading.Thread(target=udp37.listen_bytimes, args=(100,)).start()
threading.Thread(target=udp36.loop_process, args=()).start()
threading.Thread(target=udp37.loop_process, args=()).start()


tcp36_listener = TcpImformater((local_loop, listen_mainport))
tcp37_listener = TcpImformater((local_loop, listen_sport))

threading.Thread(target=tcp36_listener.listen_bytimes, args=(100,)).start()
threading.Thread(target=tcp37_listener.listen_bytimes, args=(100,)).start()
threading.Thread(target=tcp36_listener.loop_process, args=()).start()
threading.Thread(target=tcp37_listener.loop_process, args=()).start()

while 1:
    show_status(udp37)
    show_status(tcp37_listener)
    time.sleep(60)