# p2ppy p2p的一种python实现

./_peer_config  节点配置(imformater无需配置) <br>
./_protocol 项目网络的通讯协议 <br>
./imformater 一种知识节点的实现  <br>
./peer 一种成员节点实现  <br>
./tcpudp 通讯socket基类，p2p网络不同角色皆基于此编写，协议消息处理采用生产消费者模式 <br>

# 组件

* [self](http://gitlab.weicheche.cn/xuechen.han/p2ppy).
* [p2ppy] (http://gitlab.weicheche.cn/xuechen.han/WcChain_py/tree/master). <main>

# 参考文档

* [异步IO](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/00143208573480558080fa77514407cb23834c78c6c7309000).
* [Python黑魔法 --- 异步IO（ asyncio） 协程](http://python.jobbole.com/87310/).
* [p2p技术详解目录](http://www.52im.net/thread-50-1-1.html).
* [端口映射](https://blog.csdn.net/xiaoxianerqq/article/details/50363655).

# 特性和进度相关说明
## 具备的特性
 ### 网络层 完成-80%

## 已经发现的待解决/完善的问题

* 1.当需要重连其他peer的待连接阶段(处理完1011之后)，如果目标已经存在在路由表中，可以先通过路由表地址尝试，成功则可以直接维护表值而跳过穿洞过程。
* 2.udppeer.block_request 的时候,需要暂停route；或者也同化其使用底层的生产消费者模式（也许能解决block的超时挂掉进程的问题）。
  --已解决，事实证明统一走生产消费线能解决不少问题
* 3.传输分片的支持,需要包含完整度检测。
* 4.新加入节点的全量链下载,长链被同步的问题,依赖于3。
* 5.imforma间的对等机制。   暂缓实现：新入节点总得需要一个目标

## 现阶段忽略的特性

# 改动日记