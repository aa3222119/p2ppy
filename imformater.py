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
processing_nat = {}  # 进行中的端口映射对 (网络标示,消息):先前一致的端口映射  先前一致的端口映射peer也可以存下来验证
imformaters_di = {}
route_df = pd.DataFrame({'host': '0.0.0.0', 'port': listen_sport, 'phost': '0.0.0.0', 'pport': listen_sport,
                         'nattype': -1, 'update_time': now(), 'verify_taken': 0, 'p2p_times': 0,
                         }, index=[str('1')])


class UdpImformater(UdpSocket):

    def set_process_map(self, map_di):
        self.process_map = map_di

    def process_dque(self):
        if len(self.dqueue):
            mess_head, mess_body, addr = self.dqueue.popleft()
            if mess_head in self.process_map:
                callback, new_addr = self.process_map[mess_head](mess_body, addr)
                if new_addr:
                    self.send_message(callback, new_addr)
                else:
                    self.send_message(callback, addr)
            else:
                print('没注册处理函数:', mess_head)
        else:
            time.sleep(.5)
            print('dqueue clean', len(self.dqueue), len(self.dqueue), end='\r')

    def loop_process(self, times=None):
        if times is None:
            while True:
                self.process_dque()
        else:
            for i in range(times):
                self.process_dque()


def fix_route(mess, nattype, addr):
    update_time = now()
    verify_taken = update_time - mess['timestamp']
    p2p_times = 0
    if mess['address'] in route_df.index:
        p2p_times = route_df.loc[mess['address'], 'p2p_times']
    route_df.loc[mess['address']] = {'host': mess['laddr'][0], 'port': mess['laddr'][1],
                                     'phost': addr[0], 'pport': addr[1],
                                     'update_time': now(),
                                     'verify_taken': verify_taken, 'nattype': nattype,
                                     'p2p_times': p2p_times}


def handle0001(mess, addr):
    need_list = ['laddr', 'address', 'timestamp']
    try:
        mess = eval(mess)
        if all([x in mess for x in need_list]):
            if mess['laddr'] == addr:
                fix_route(mess, 0, addr)
                return str(routein_finish), None
            else:
                processing_nat.update({(mess['address'], routein_no1): (mess['laddr'], addr)})
                return str(routein_no2), None
        else:
            mind_mess = '缺少信息(%s)' % '/'.join(need_list)
            return str(routein_failed) + mind_mess, None
    except Exception as err:
        print(err)


def handle0002(mess, addr):
    need_list = ['laddr', 'address', 'timestamp', 'last_process_key']
    try:
        mess = eval(mess)
        if all([x in mess for x in need_list]):
            if mess['last_process_key'] not in processing_nat:
                return str(routein_no1), None
            last_process_value = processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], addr):
                processing_nat.update({(mess['address'], routein_no2): last_process_value})
                return str(routein_no3), None
            else:
                fix_route(mess, 4, addr)
                return str(routein_finish)
        else:
            mind_mess = '缺少信息(%s)' % '/'.join(need_list)
            return str(routein_failed) + mind_mess, None
    except Exception as err:
        print(err)


def handle0003(mess, addr):
    need_list = ['laddr', 'address', 'timestamp', 'last_process_key']
    try:
        mess = eval(mess)
        if all([x in mess for x in need_list]):
            if mess['last_process_key'] not in processing_nat:
                return str(routein_no1), None
            last_process_value = processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], addr):
                processing_nat.update({(mess['address'], routein_no3): last_process_value})
                return str(routein_no4), None
            else:
                fix_route(mess, 3, addr)
                return str(routein_finish), None
        else:
            mind_mess = '缺少信息(%s)' % '/'.join(need_list)
            return str(routein_failed) + mind_mess, None
    except Exception as err:
        print(err)


def handle0004(mess, addr):
    need_list = ['laddr', 'address', 'timestamp', 'last_process_key', 'paddr']
    try:
        mess = eval(mess)
        if all([x in mess for x in need_list]):
            imformaters_di[addr] = None
            if mess['last_process_key'] not in processing_nat:
                return str(routein_no1), None
            last_process_value = processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], mess['paddr']):
                fix_route(mess, 1, last_process_value[1])
                return str(routein_finish), last_process_value[1]
            else:
                fix_route(mess, 2, last_process_value[1])
                return str(routein_finish), last_process_value[1]
        else:
            mind_mess = '缺少信息(%s)' % '/'.join(need_list)
            return str(routein_failed) + mind_mess, None
    except Exception as err:
        print(err)


def handle3004(mess, addr):
    need_list = ['laddr', 'address', 'timestamp', 'oaddr']
    try:
        mess = eval(mess)
        if all([x in mess for x in need_list]):
            oaddr = mess.pop('oaddr')
            mess['paddr'] = addr
            return str(routein_no4) + str(mess), oaddr
        else:
            mind_mess = '缺少信息(%s)' % '/'.join(need_list)
            return str(routein_failed) + mind_mess, None
    except Exception as err:
        print(err)


def show_status():
    print('processing_nat', processing_nat, end='\n')
    route_df_show = route_df.copy()
    route_df_show['dt_'] = now() - route_df_show['update_time']
    print(route_df_show, end='\n')

# playgroundimport time

udp36 = UdpImformater((local_loop, listen_mainport))
udp37 = UdpImformater((local_loop, listen_sport))

start = now()
threading.Thread(target=udp36.listen_bytimes,args=(100,)).start()
threading.Thread(target=udp37.listen_bytimes,args=(100,)).start()
udp36.set_process_map({routein_no1: handle0001, routein_no2: handle0002, routein_no3: handle0003,
                       routetransfer_no4: handle3004
                       })
udp37.set_process_map({routein_no3: handle0003, routein_no4: handle0004,
                       routetransfer_no4: handle3004
                       })
threading.Thread(target=udp36.loop_process,args=()).start()
threading.Thread(target=udp37.loop_process,args=()).start()

while 1:
    show_status()
    time.sleep(30)