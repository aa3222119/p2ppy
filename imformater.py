# ===========================================
# @Time    : 2018/5/18 17:12
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : imformater.py
# @Software: PyCharm Community Edition
# ===========================================

# from hashlib_func import *
from tcpudp import *
from protocol_ import *
from random import randint

import time, threading
now = lambda: time.time()


listen_mainport = 10036
listen_sport = 10037
local_loop = '0.0.0.0'
imformaters_di = {}

route_df_template = pd.DataFrame({}, columns=['address', 'host', 'port', 'phost', 'pport', 'napttype',
                                              'update_time', 'verify_taken', 'p2p_times',
                                              'napt_start', 'napt_clue', 'napt_speed', 'clue_time', 'clue_times'])
route_df_template.set_index('address', inplace=True)

need_list = ['laddr', 'address', 'timestamp']
need_list1002 = need_list + ['last_process_key']   # 1003也是它
need_list3004 = need_list1002 + ['oaddr']
need_list1004 = need_list1002 + ['paddr']


class UdpImformater(UdpSocket):

    route_df = route_df_template.copy(deep=True)
    processing_nat = {}  # 进行中的端口映射对 (网络标示,消息):先前一致的端口映射  先前一致的端口映射peer也可以存下来验证

    def handle1010(self, mess, addr, soc_object):
        mess = eval(mess)
        # this_df = self.route_df.query("phost=='%s'&pport==%s" % addr).reset_index()  # 1010的发起者
        # if len(this_df):
        if mess['address'] in self.route_df.index:
            this_df = self.route_df.loc[mess['address']].to_dict()
            dt = now() - this_df['update_time']
            # 需要99s内更新过自己的route才能请求peer
            if dt < 99:
                # 符合条件的待定peer
                possi_rou_df = self.route_df.query("napttype<5&address!='%s'" % mess['address']).reset_index()  # 还缺少一些筛选 知识节点还需要维护一张图
                if len(possi_rou_df):
                    tar_row = possi_rou_df.loc[randint(0, len(possi_rou_df)-1)]  # 目标peer 加上随机数
                    # 总是先通知被动方先准备 被动方为napttype更小的那边
                    # 请求1010的地址为para: addr; 其napttype为para:  this_df['napttype']
                    # 目标peer的地址为: (tar_row['phost'], tar_row['pport']);  其napttype为para: tar_row['napttype']
                    if tar_row['napttype'] <= this_df['napttype']:
                        mess_to_tar = {'peer_addr': addr, 'peer_napttype': this_df['napttype'],
                                       'napt_clue': this_df['napt_clue'],
                                       'napt_speed': this_df['napt_speed'],
                                       'clue_dt': now() - this_df['clue_time'],
                                       'peer_address': mess['address']}
                        addr = (tar_row['phost'], tar_row['pport'])  # 切换发送到目标peer
                    else:
                        mess_to_tar = {'peer_addr': (tar_row['phost'], tar_row['pport']),
                                       'peer_napttype': tar_row['napttype'],
                                       'napt_clue': tar_row['napt_clue'],
                                       'napt_speed': tar_row['napt_speed'],
                                       'clue_dt': now() - tar_row['clue_time'],
                                       'peer_address': tar_row['address']}
                    mess_response = str(notify_conn) + str(mess_to_tar)
                else:
                    mess_response = str(no_peers)
            else:
                mess_response = str(expired_route) + '未及时更新(dt=%s)' % dt
        else:
            mess_response = str(no_route)
        self.send_message(mess_response, addr, soc_object)

    def handle1011(self, mess, addr, soc_object):
        mess = eval(mess)
        passive_napt = mess.pop('passive_napt')
        # print('交换转发', mess, addr, soc_object)
        addr, mess['peer_addr'] = mess['peer_addr'], addr
        mess['peer_napttype'] = passive_napt
        mess_response = str(suit_peers) + str(mess)
        self.send_message(mess_response, addr, soc_object)


class TcpImformater(TcpSocket):

    route_df = route_df_template.copy()
    processing_nat = {}  # 进行中的端口映射对 (网络标示,消息):先前一致的端口映射  先前一致的端口映射peer也可以存下来验证

    def handle3004(self, mess, addr, soc_object):  # Tcp 需要不同的socket来转发
        self.binded_speaker.dqueue.append((3004, mess, addr, None))


def fix_route(self, mess_di, napttype, addr):
    verify_taken = now() - mess_di['timestamp']
    upd_dict = {'host': mess_di['laddr'][0], 'port': mess_di['laddr'][1], 'phost': addr[0], 'pport': addr[1],
                'update_time': now(), 'verify_taken': verify_taken, 'napttype': napttype, 'p2p_times': 0,
                'napt_start': 12000, 'napt_clue': 10000, 'napt_speed': 100.0, 'clue_time': -1, 'clue_times': 0}
    # 更新路由表已有记录
    if mess_di['address'] in self.route_df.index:
        upd_cloumns = ['p2p_times', 'napt_start', 'napt_clue', 'napt_speed', 'clue_time', 'clue_times']
        row = self.route_df.loc[mess_di['address'], upd_cloumns]
        upd_dict.update(row.to_dict())
        self.route_df.drop(mess_di['address'], inplace=True)
    self.route_df.loc[mess_di['address']] = upd_dict


def handle1001(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list]):
        if mess['laddr'] == addr:
            self.fix_route(mess, 0, addr)
            mess_response = str(routein_finish) + str({'napttype': 0})
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
    if all([x in mess for x in need_list1002]):
        if mess['last_process_key'] not in self.processing_nat:
            mess_response = str(routein_no1)
        else:
            last_process_value = self.processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], addr):
                self.processing_nat.update({(mess['address'], routein_no2): last_process_value})
                mess_response = str(routein_no3)
            else:
                self.fix_route(mess, 4, last_process_value[1])
                mess_response = str(routein_finish) + str({'napttype': 4})
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle1003(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list1002]):
        if mess['last_process_key'] not in self.processing_nat:
            mess_response = str(routein_no1)
        else:
            last_process_value = self.processing_nat.pop(mess['last_process_key'])
            if last_process_value == (mess['laddr'], addr):
                self.processing_nat.update({(mess['address'], routein_no3): last_process_value})
                mess_response = str(routein_no4)
            else:
                self.fix_route(mess, 3, last_process_value[1])
                mess_response = str(routein_finish) + str({'napttype': 3})
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle1004(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list1004]):
        imformaters_di[addr] = None   # 由于1004消息一定来自于其他imforma转发
        if mess['last_process_key'] not in self.processing_nat:
            mess_response = str(routein_no1)
        else:
            last_process_value = self.processing_nat.pop(mess['last_process_key'])
            nattype = 1 if last_process_value == (mess['laddr'], mess['paddr']) else 2
            self.fix_route(mess, nattype, last_process_value[1])
            # last_process_value[1] 存储的是1003时的paddr
            mess_response, addr = str(routein_finish)+ str({'napttype': nattype}), last_process_value[1]
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


@genel_try_dec
def handle3004(self, mess, addr, soc_object):
    mess = eval(mess)
    if all([x in mess for x in need_list3004]):
        mess['paddr'] = addr
        addr = mess.pop('oaddr')
        mess_response = str(routein_no4) + str(mess)
    else:
        mind_mess = '缺少信息(%s)' % '/'.join(need_list)
        mess_response = str(routein_failed) + mind_mess
    self.send_message(mess_response, addr, soc_object)


def handle1009(self, mess, addr, soc_object):
    """路由表线索clue维护
        napttype 2 3 4 的时候需要"""
    mess = eval(mess)
    address = mess['address']
    if len(self.route_df.loc[address]):
        if self.route_df.loc[address, 'clue_time'] > 0:
            during_seconds = mess['timestamp'] - self.route_df.loc[address, 'clue_time']
            during_ports = addr[1] - self.route_df.loc[address, 'napt_clue']
            if during_ports > 0:  # 小于零的时候: 为65535一个周期用完又从10000(一般而言)附近开始 ,可以不必更新
                self.route_df.loc[address, 'napt_speed'] = during_ports / during_seconds
        self.route_df.loc[address, 'napt_clue'] = addr[1]
        if addr[1] < self.route_df.loc[address, 'napt_start']:
            self.route_df.loc[address, 'napt_start'] = addr[1]
        self.route_df.loc[address, 'clue_times'] += 1
        self.route_df.loc[address, 'clue_time'] = mess['timestamp']


# 动态方法加载
UdpImformater.fix_route = fix_route
UdpImformater.handle1001 = handle1001
UdpImformater.handle1002 = handle1002
UdpImformater.handle1003 = handle1003
UdpImformater.handle1004 = handle1004
UdpImformater.handle3004 = handle3004
UdpImformater.handle1009 = handle1009


TcpImformater.fix_route = fix_route
TcpImformater.handle1001 = handle1001
TcpImformater.handle1002 = handle1002
TcpImformater.handle1003 = handle1003
TcpImformater.handle1004 = handle1004


class TcpImformaSpeak(TcpImformater):

    name = 'TcpImformaSpeaker'

TcpImformaSpeak.handle3004 = handle3004


@polling_dec(dt=60)
def show_status(imformater):
    print('**********show_status**********  ', imformater, '.processing_nat', imformater.processing_nat, end='\n')
    route_df_show = imformater.route_df.copy()
    route_df_show['dt_update'] = now() - route_df_show['update_time']
    route_df_show['dt_clue'] = now() - route_df_show['clue_time']
    print(route_df_show, end='\n')
    print('********************************  ')


# -------------------------------------------------------------playground-------------------------------------------------------------
if __name__ == "__main__":
    start = now()

    udp36 = UdpImformater((local_loop, listen_mainport))
    udp37 = UdpImformater((local_loop, listen_sport))
    threading.Thread(target=udp36.listen_bytimes, args=()).start()
    threading.Thread(target=udp37.listen_bytimes, args=()).start()
    threading.Thread(target=udp36.loop_process, args=()).start()
    threading.Thread(target=udp37.loop_process, args=()).start()

    # tcp36_listener = TcpImformater((local_loop, listen_mainport))
    # tcp37_listener = TcpImformater((local_loop, listen_sport))
    # tcp_speak = TcpImformater()
    # tcp36_listener.binded_speaker = tcp_speak
    #
    # threading.Thread(target=tcp36_listener.listen_bytimes, args=()).start()
    # threading.Thread(target=tcp37_listener.listen_bytimes, args=()).start()
    # threading.Thread(target=tcp36_listener.loop_process, args=()).start()
    # threading.Thread(target=tcp37_listener.loop_process, args=()).start()
    # threading.Thread(target=tcp_speak.loop_process, args=()).start()
    threading.Thread(target=show_status, args=(udp37, )).start()
