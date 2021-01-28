# 基于Websockets的命令行聊天室(or游戏房间)

##  依赖

1. Python 3.7+

2. websockets 库

   ```shell
   pip3 install websockets
   ```

（以上两条依赖对于客户端和服务器端都适用）

## 概述

基于websockets提供的接口，使用异步消息队列，实现通信。服务器端(<b>server.py</b>)可以同时与多个客户端(<b>client.py</b>)建立连接，对每个客户端发来的消息进行响应（回复该客户端、转发给其余客户端、生成系统提示消息等）。

客户端需要指定服务器IP地址和端口来连接到服务器，可以选择一个用户名在聊天/游戏中显示。服务器端会按接入先后顺序给每个客户分配一个ID(由先到后为1，2，3...)，ID不会重复，但对于断开连接的客户，暂时不会回收其ID。

修改client.py中的内容，指定服务器IP、服务器端口、自己的用户名后，在命令行中运行client.py（不用加参数），程序会尝试连接到服务器。连接到服务器后，客户端程序会持续从sys.stdin请求输入，用户输入消息并按下回车，消息会被发送给服务器。服务器给用户的消息则会被print到命令行。输入EXIT，连接会被安全断开，程序正常结束。

## API

server.py中只提供服务器端的通信服务，聊天室/游戏等业务逻辑需要由下游开发人员(您)在<b>logic.py</b>中实现，API如下：

您只需在与server.py位于同文件夹下创建名为<b>logic.py</b>的python脚本，在其中实现如下三个函数即可：

```python
def logic(id:int, lookup:dict, message:str) -> dict:
	#...

def logic_client_connect(id:int, lookup:dict) -> dict:
    #...

def logic_client_disconnect(id:int, name:str, lookup:dict) -> dict:
    #...
```

三个函数的返回值都应为python字典类型，每个键值对为(id:int, reply:str)的形式，含义为命令server.py给ID为id的用户发送内容为reply的消息。换言之，这三个函数定义了不同情况下服务器需要向哪些用户发送什么消息。下面描述这三个函数的调用时机和参数含义。

当任意已连接的用户(ID为id)向服务器发送内容为message消息时，第一个函数<b>logic</b>都会被调用。lookup为一个字典，记录了调用此函数的时刻服务器上有多少用户，其ID和用户名各为什么。每个键值对为(id:int, name:str)的形式，将用户ID映射到用户名，下同。

当有ID为id的新用户连接到服务器时，第二个函数<b>logic_client_connect</b>会被调用。传入的lookup字典已经记录了新用户的信息。

当ID为id，用户名为name的用户与服务器断开连接时，第三个函数<b>logic_client_disconnect</b>会被调用。传入的lookup字典中，断开连接的用户的信息已经被抹去。

## 示例

仓库中的logic.py为一个示例，它实现了斗地主游戏的游戏逻辑，兼具聊天室的功能。本地测试时，将logic.py与server.py放在同一文件夹下，运行server.py(不用加参数)即可提供服务。在命令行中运行客户端client.py，即可与服务器连接。可以在多个命令行窗口运行client.py，模拟多用户的情形。