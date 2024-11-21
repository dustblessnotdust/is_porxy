免责声明，本脚本仅供学习使用，只做学习交流，其他均与本人，切勿触碰法律底线，否则后果自负！！！！

## 永久代理池思路
全网查找可用ip，不可能没有ip可用
- 首先使用zmap获取全网ip，zmap不会的可以看：[zmap详解，安装+详细使用](https://blog.csdn.net/2202_75361164/article/details/143899506)
- 之后进行初次筛选，这个初次筛选一般以后就作为最大的ip池
- 之后进行细致筛选，这个时候，ip地址可以几天就会有变化，可以以前不能使用的现在可以了，以前可以的现在不行了，所以写一个定时脚本，定时更新就行

## ip_porxy使用
首先，我们先进行初次筛选
使用ip_porxy工具初次验证存活ip
```
usage: is_porxy.py [-h] [-f FILE] [-p PORT] [-o OUTPUT] [-t THREADS] [-s SAVE_INTERVAL]

验证IP地址作为代理的有效性。

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  包含IP地址的输入文件（默认: ips.txt）
  -p PORT, --port PORT  要测试的端口号（如果指定了 -af 参数，则此参数无效）
  -o OUTPUT, --output OUTPUT
                        保存有效代理的输出文件前缀（默认: 第一个IP地址的A段_端口号）
  -t THREADS, --threads THREADS
                        使用的线程数（默认: 10）
  -s SAVE_INTERVAL, --save-interval SAVE_INTERVAL
                        每次探测得到多少个IP后写入文件（默认: 100）

```

## 常用命令
```
python3 .\is_porxy.py -h

python3 .\is_porxy.py -p 80 -f .80.txt -s 100 -o 80.txt

python3 .\is_porxy.py -p 80 -f .80.txt -s 100 -o 80.txt -t 100 # -t 100 对电脑来说负担有点大，推荐在4核及以上服务器上跑，跑满可以开到500
```



