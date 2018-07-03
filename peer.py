# ===========================================
# @Time    : 2018/5/21 15:23
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : peer.py
# @Software: PyCharm Community Edition
# ===========================================

# from hashlib_func import *
from tcpudp import *
from _peer_config import *
from protocol_ import *
import threading
# sys.path.append('../WcChain_py')
# import blockchain


# 生成自己的address, 应通过加密模块获取,  模拟先取 sys.argv[1]

host_loop = getip_(0)[0]
# print('host_loop', host_loop)
laddr = (host_loop, 10036)
laddr_sender = (host_loop, 10038)

if len(sys.argv) < 2:
    sys.argv.append(' beta antony')
address = host_loop + str(sys.argv[1])
# address = sha2str(host_loop + str(sys.argv[1]))[:32]
address = address if type(address) is str else address.decode()

mess_di_template = {'address': address, 'laddr': laddr}

# 知识节点
imformater_list = [('47.104.190.254', 10036), ('120.77.65.191', 10036), ('120.25.245.164', 10036)]

# peer维护的连接路由表
route_df_template = pd.DataFrame({}, columns=['address', 'phost', 'pport', 'begin_time', 'update_time',])
route_df_template.set_index('address', inplace=True)

main_imformater = imformater_list.pop(0)
sub_imformater = imformater_list.pop(0)
# 一些可能用到的全局变量
gloparas = {'napttype': None,
            'last_imforma': None,
            'testing_flag': False}

# addr2str = lambda h, p: '%s:%s' % (h, p)
# str2addr = lambda x: s.split(':')


# subt_  subthread
def subt_peer_testing(obj_send_func, addr, port_end=65535):
    """testing_flag 在做预留时无用，但是在主动方连接时则有用；
       由于是消费者模式，同时最多只可能有一个子进程处理，所以用gloparas是进程安全的"""
    gloparas['testing_flag'] = True
    port_end = port_end if port_end < 65536 else 65535
    mess_send = str(success_hole_flag) + str(mess_di_template)
    while gloparas['testing_flag'] and addr[1] < port_end:
        addr = (addr[0], addr[1] + 1)
        gevent.sleep(0.005)
        obj_send_func(mess_send, addr)
        

def subt_route_clue_send(obj_send_func, addr):
    mess_di = mess_di_template.copy()
    mess_di['timestamp'] = now()
    obj_send_func(str(routein_clue) + str(mess_di), addr)
    gevent.sleep(20)
    mess_di['timestamp'] = now()
    obj_send_func(str(routein_clue) + str(mess_di), addr)


class UdpPeer(UdpSocket):
    route_df = route_df_template.copy()
    mess_di = mess_di_template.copy()

    @genel_try_dec
    def handle1002(self, mess, addr, soc_object):
        self.mess_di['last_process_key'] = (self.mess_di['address'], routein_no1)
        self.send_message(str(routein_no2) + str(self.mess_di), addr, soc_object)

    @genel_try_dec
    def handle1003(self, mess, addr, soc_object):
        self.mess_di['last_process_key'] = (self.mess_di['address'], routein_no2)
        addr = (main_imformater[0], main_imformater[1]+1)
        self.send_message(str(routein_no3) + str(self.mess_di), addr, soc_object)

    @genel_try_dec
    def handle1004(self, mess, addr, soc_object):
        self.mess_di['last_process_key'] = (self.mess_di['address'], routein_no3)
        self.mess_di['oaddr'] = (main_imformater[0], main_imformater[1] + 1)
        addr = sub_imformater
        self.send_message(str(routetransfer_no4) + str(self.mess_di), addr, soc_object)

    # peer常规的阻塞(block)发送数据请求方式
    def block_request(self, mess, addr):
        try:
            self.send_message(mess, addr)
            return self.recv_handle(lambda m, a: (m, a), with_spawn=False)  # 此步骤在time out的时候只返回一个None
        except:
            print('block_request no response!!')
            return 0

    def handle1010(self, mess, addr, soc_object):  # 收到1010的peer表示是要主动连接的,且此时被动方已经准备好了
        mess = eval(mess)
        print('peer收到imforma的1010,主动发起连接', mess)
        addr = mess['peer_addr']
        if mess['peer_napttype'] in [0, 1]:
            mess_send = str(success_hole_flag) + str(mess_di_template)
            self.send_message(mess_send, addr)
        # 对方已经预留session, 目标是找到这个session
        elif mess['peer_napttype'] in [2]:
            tmp_udp = UdpPeer()
            # tmp_udp.send_message(str(askim_route) + str({'addr': mess['peer_addr']}), main_imformater)
            # mess_ = tmp_udp.recv_handle(lambda mess_, _: mess_, with_spawn=False)  # 包含需要用到的peer clue信息
            mess_, _ = tmp_udp.block_request(str(askim_route) + str({'addr': mess['peer_addr']}), main_imformater)
            port_end = int(mess_['napt_clue'] + 2 * mess_['napt_speed'] * mess_['clue_dt'])  # 预判的对方网关端口范围的终点
            addr_st = (mess_['peer_addr'][0], mess_['napt_clue'])  # 预判的对方网关端口范围起点(addr的格式)
            print('碰撞预留session::', mess, addr_st, port_end)
            threading.Thread(target=subt_peer_testing, args=(self.send_message, addr_st, port_end)).start()

    def handle1011(self, mess, addr, soc_object):  # 收到1011的peer表示是需要被动准备的
        """被动连接说明自己的类型近0, 是先准备的那个peer
        """
        mess = eval(mess)
        # 先不管ip啦 考虑address作为唯一标识重复 后要解决
        if mess['peer_address'] in self.route_df.index:
            if now() - self.route_df.loc[mess['peer_address'], 'update_time'] < 300:
                print('peer_address(%s)在已通信的路由表中' % mess['peer_address'])
                return 0
        # 虽然端口映射session不变, 但要解决不先发送不会被网关转发进来的问题
        if gloparas['napttype'] in [1, 2]:   # 此不管peer的端口号都对应一致的session
            port_end = int(mess['napt_clue'] + 2*mess['napt_speed']*mess['clue_dt'])  # 预判的对方网关端口范围的终点
            addr_st = (mess['peer_addr'][0], mess['napt_clue'])  # 预判的对方网关端口范围起点(addr的格式)
            print('#1011 预留session以保证可被网关转发:', mess, addr_st, port_end)
            threading.Thread(target=subt_peer_testing, args=(self.send_message, addr_st, port_end)).start()
            # self.send_message(str(notify_conn), mess['peer_addr'], soc_object)
        elif gloparas['napttype'] in [3, 4]:
            print('#1011 更好napt的都已经是3/4了 比较复杂 几乎不能实现')
        else:
            print('#1011 本机不需要跨越NAPT 可直接被连接...')
        mess.update({'passive_napt': gloparas['napttype']})
        self.send_message(str(notify_conn) + str(mess), addr, soc_object)

    def fix_route(self, mess, addr):
        # this_df = self.route_df.query("phost=='%s'&pport==%s" % addr)
        mess = eval(mess)
        if 'address' in mess:
            address_ = mess['address']
            upd_dict = {'phost': addr[0], 'pport': addr[1], 'update_time': now(), 'begin_time': now()}
            if address_ in self.route_df.index:
                row = self.route_df.loc[address_, ['begin_time']]
                upd_dict.update(row.to_dict())
                self.route_df.drop(address_, inplace=True)
            self.route_df.loc[address_] = upd_dict
            print(self.route_df)
        else:
            print('peer fix route 缺少信息')

    def handle1013(self, mess, addr, soc_object):
        mess_send = str(success_hole_flag_rev) + str(mess_di_template)
        self.send_message(mess_send, addr, soc_object)
        self.fix_route(mess, addr)

    def handle1014(self, mess, addr, soc_object):
        gloparas['testing_flag'] = False
        self.fix_route(mess, addr)


class TcpPeer(TcpSocket):

    def send_message(self, message, addr, soc_object=None):
        soc_object = super(TcpPeer,self).send_message(message, addr, soc_object=None)
        # id(self.soc) = id(soc_object) 相等哦
        data = soc_object.recv(1024, )
        print(data)
        self.mess_tudeque(data, addr, )

    def handle1002(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no1)
        self.re_bind()
        self.send_message(str(routein_no2) + str(mess_di), addr, )

    def handle1003(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no2)
        addr = (main_imformater[0], main_imformater[1] + 1)
        self.re_bind()
        self.send_message(str(routein_no3) + str(mess_di), addr, soc_object)

    def handle1004(self, mess, addr, soc_object):
        mess_di['last_process_key'] = (mess_di['address'], routein_no3)
        mess_di['oaddr'] = (main_imformater[0], main_imformater[1] + 1)
        addr = sub_imformater
        self.re_bind()
        self.send_message(str(routetransfer_no4) + str(mess_di), addr, soc_object)


def handle1005(self, mess, addr, soc_object):
    if mess:
        mess = eval(mess)
        gloparas.update(mess)
        gloparas['last_imforma'] = addr[0]
    # 路由表线索clue维护,当napttype为 2 3 4 时需要
    if gloparas['napttype'] in [2, 3, 4]:
        # threading.Thread(target=subt_route_clue_send, args=(UdpPeer().send_message, addr)).start()
        subt_route_clue_send(UdpPeer().send_message, addr)


def handle1006(self, *args):
    print('1006', self, *args)


# 动态方法加载
UdpPeer.handle1005 = handle1005
TcpPeer.handle1005 = handle1005
UdpPeer.handle1006 = handle1006
TcpPeer.handle1006 = handle1006

udp36 = UdpPeer(laddr, )
# tcp36 = TcpPeer(laddr, )


@polling_dec()
def show_status(peer):
    print('**********show_status**********  ', peer, end='\n')
    route_df_show = peer.route_df.copy()
    route_df_show['dt_update'] = now() - route_df_show['update_time']
    route_df_show['dt_during'] = route_df_show['update_time'] - route_df_show['begin_time']
    print(route_df_show, end='\n')
    print('********************************  ')


@polling_dec(dt=45)
def route_in():
    mess_di = mess_di_template.copy()
    mess_di['timestamp'] = now()
    udp36.mess_di = mess_di
    udp36.send_message(str(routein_no1) + str(mess_di), main_imformater)


@polling_dec(DT_second['suit_peers'])
def conn_peer():
    mess_di = mess_di_template.copy()
    mess_di['timestamp'] = now()
    print('发起:', str(suit_peers) + str(mess_di))
    udp36.send_message(str(suit_peers) + str(mess_di), main_imformater)


def deploy_peer(with_handle=True):
    # 作为服务的节点
    if with_handle:
        threading.Thread(target=udp36.listen_bytimes, args=()).start()
        threading.Thread(target=udp36.loop_process, args=()).start()
    # route_in进程
    threading.Thread(target=route_in, args=()).start()
    # show_status进程
    threading.Thread(target=show_status, args=(udp36, )).start()
    # 根据配置 连接其他peer进程
    if DT_second['suit_peers'] > 10:
        threading.Thread(target=conn_peer, args=()).start()


if __name__ == "__main__":
    deploy_peer()
