# ===========================================
# @Time    : 2018/6/13 11:31
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : .peer_config.py
# @Software: PyCharm Community Edition
# ===========================================

# DT表示发起code的时间间隔(s),

DT_second = {'suit_peers': 59,  # 向imforma询问可用peer，小于10s表示不主动发起
             'peer_mining': 31,  # 挖矿的时间间隔, 大于30的取值表示不挖矿
             'peer_mining_delay': 1800  # 第一次开始挖矿的延迟
             }

Bool_test_ground = False  # 临时测试功能开关
