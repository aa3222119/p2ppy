# p2p-python

./XX  XX <br>


###### XXX

 ./XXX : XXX <br>
 ./XXX : XXX<br>

# 参考文档

* [异步IO](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/00143208573480558080fa77514407cb23834c78c6c7309000).
* [Python黑魔法 --- 异步IO（ asyncio） 协程](http://python.jobbole.com/87310/).
* [p2p技术详解目录](http://www.52im.net/thread-50-1-1.html).
* [端口映射](https://blog.csdn.net/xiaoxianerqq/article/details/50363655).


# 发现的待优化问题

* 1.当需要重连其他peer的待连接阶段(处理完1011之后)，如果目标已经存在在路由表中，可以先通过路由表地址尝试，成功则可以直接维护表值而跳过穿洞过程。
* 2.udppeer.block_request 的时候,需要暂停route；或者也同化其使用底层的生产消费者模式（也许能解决block的超时挂掉进程的问题）。
  --已解决，事实证明统一走生产消费线能解决不少问题
* 3.传输分片的支持,需要包含完整度检测。
* 4.新加入节点的全量链下载,长链被同步的问题,依赖于3。
* 5.imforma间的对等机制。   暂缓实现：新入节点总得需要一个目标