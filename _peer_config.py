# ===========================================
# @Time    : 2018/6/13 11:31
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : .peer_config.py
# @Software: PyCharm Community Edition
# ===========================================

# DT表示发起code的时间间隔(s),
# suit_peers : 向imforma询问可用peer，小于10s表示不主动发起,
# peer_mining : 挖矿的时间间隔, 大于30的取值表示不挖矿
# peer_mining_delay 第一次开始挖矿的延迟
DT_second = {'suit_peers': 59,
             'peer_mining': 3,
             'peer_mining_delay': 0}

Bool_test_ground = True
