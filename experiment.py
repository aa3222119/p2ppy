# ===========================================
# @Time    : 2018/5/19 17:26
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : experiment.py
# @Software: PyCharm Community Edition
# ===========================================
from peer import *

udp136 = UdpPeer(laddr, 4)
udp136.send_message('8001准备超时的', main_imformater)
print(udp136.recv_handle(lambda m, a: (m, a), with_spawn=False))
print(udp136)