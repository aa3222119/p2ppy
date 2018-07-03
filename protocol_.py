# ===========================================
# @Time    : 2018/5/22 19:21
# @Author  : antony
# @Email   : 502202879@qq.com
# @File    : protocol_.py
# @Software: PyCharm Community Edition
# ===========================================
# NAT类型定义：特殊地,我们把直接具有公网ID的节点定为类型0;1：全锥形;2：受限全锥形;3：端口受限全锥形;4：对称型
#
# imformater节点 在网络中需要有大于1的的节点, imformater之间是对等的, 负责存储更新网络中peer节点和对应的NAT类型, 测试阶段都存储在内存中
# 负责peer申请2p连接时的策略和调度问题,
# imformater节点监听两个端口 10036 10037, 主要工作在10036节点
# routein_mess :
# peer节点发送网络位置注册最多需要发送4条routein_mess,其中前3条是发给imformater_A, 需要确认是否类型1时发送第四条给B
# routein_mess中的前两条是发给imformater_A：10036端口,
# 1.通过第一条检查端口映射, 若不存在映射关系则为类型0,
# 2.存在则对比第二条的端口映射, 不一致则定为类型4;
#   3.若一致则发送第3条routein_mess到imformater_A：10037端口, 若端口映射不一致则定为类型3;
#      4.若一致则需要发第4条routein_mess到imformater_B：10036端口, 若不一致则定为类型2; 一致则定为类型1.
#

routein_no1 = 1001
routein_no2 = 1002
routein_no3 = 1003
routein_no4 = 1004
# 对应route_in的步骤1234
# 对应角色不同：一般imformater发送则表示请求节点的该过程；而peer发送则表示route_in的动作
#  所以一般不会有imformater 发送routein_no1  routein_no1由peer主动请求。除开imformater是否有主动找peer更新route的机制特殊约定

routetransfer_no4 = 3004  # route_in 第4阶段的转发消息, 由peer发送给sub_imformater , sub_imformater处理该消息转发
routein_finish = 1005   #
routein_failed = 1006
routein_clue = 1009  # 由peer发给imforma 使得imforma形成route clue   一般由peer的子线程完成，两次且间隔一定时长


# 101X p2p相关编码 只用UDP处理
suit_peers = 1010  # 可以连接的peers 由peer向imforma请求 , imforma回复同样序号的确认消息，附带已待连接的peer
notify_conn = 1011  # peer连接通知  由imforma通知peer具体的连接准备,  peer回复同样的序号表示准备ok
easyside_hole = 1012  # napttype靠前的预留穿洞  由peer通知另一个peer(一般不会收到)   直到收到success_hole_flag表示成功
success_hole_flag = 1013  # peer主动方和被动方(做预留时)发送给另一peer 
success_hole_flag_rev = 1014  # 收到 success_hole_flag 后返回success_hole_flag_rev 确认连接
code_err_101X = 1019
success_conn = 1020  # 由主动连接的peer发向被动的peer 发送表示,,,收到表示连接成功,  返回同样的序号形成相互确认, 表示做好继续互通消息的准备

# ------------------------------------ 6开头表示所有peer向imforma的普通内容请求   -----------------------------------------------
askim_route = 6001         # 查询路由表信息，需提供必要参数，UDP时peer一般是直接阻塞获取相关信息

# -------------------------------------- 8开头表示所有peer之间的普通内容请求   --------------------------------------------------
askpeer_wcchain = 8001     # 请求链相关信息，由参数URL决定请求内容

# ----------------------------------- 9开头表示peer对8XXX的回复，或广播的信息   -------------------------------------------------
respeer_wcchain = 9001     # 对9001的相应回复
broadcastpeer = 9002       # 向其他节点广播信息，包括由参数URL决定的内容和内容的值content

# ---------------------------------------------- 4开头的code统统代表错误   ----------------------------------------------------
no_route = 4001  # 没注册的路由 由imforma通知peer
expired_route = 4005  # 过期的路由 由imforma通知peer
no_peers = 4010  # 没有可用的peers 由imforma通知peer
