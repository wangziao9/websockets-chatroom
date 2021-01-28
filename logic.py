import random

help = '''
    您已成功连接网络斗地主游戏服务器，服务器已为您分配了整数的ID（您是第ID号用户）。
    查看服务器上所有用户:输入指令"WHO"，返回一个{编号:用户名}的字典。
    聊天(广播):如果您输入的字符串不以A-Z0-9开头，则服务器将其视为聊天，服务器上所有用户都会收到该消息。
    加入游戏:输入指令"JOIN"加入等待区，等待区满三人即可开始游戏。若服务器上已经有对局，需要等待已有对局结束再加入。
    查看手牌:输入指令"PEEK"。
    出牌:将要出的手牌用空格隔开即可，如"3 3 3 BlackJoker"。若不出则输入指令"BUCHU"。服务器不负责检查牌型是否合法。
    退出:输入指令"EXIT"。若您在游戏进行时退出，将被直接判负。
'''

class Game():
    def __init__(self, data):
        self.data = data.copy() #0~53
        self.K_number = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
        self.K_color = ['红桃','黑桃','方片','草花']
    def addcards(self, data):
        self.data.extend(data)
        self.data.sort()
    def charfor(self, x:int) -> str:
        if(x<52):
            return self.K_number[int(x/4)] #self.K_color[x%4]
        elif(x==52):
            return 'BlackJoker'
        elif(x==53):
            return 'RedJoker'
    def getcards(self) -> str:
        self.data.sort()
        ret = ""
        for i,card in enumerate(self.data):
            ret = ret + self.charfor(card) + " "
        return ret
    def usecards(self, coll) -> bool:#coll:List[str]
        data_after = self.data.copy()
        for word in coll:
            used = False
            for card in data_after:
                if self.charfor(card)==word:
                    data_after.remove(card)
                    used = True
                    break
            if not used:
                return False
        self.data = data_after
        return True

players = dict()
player_order = list()
def rotate(x):#x:List[int]
    cur = x[0]
    del x[0]
    x.append(cur)
carddeck = [i for i in range(54)]
random.shuffle(carddeck)
waiting = 0
gameon = False
landlord = -1

def global_init():
    global players,player_order,carddeck,waiting,gameon,landlord
    players = dict()
    player_order = list()
    carddeck = [i for i in range(54)]
    random.shuffle(carddeck)
    waiting = 0
    gameon = False
    landlord = -1

def logic_client_disconnect(player_id:int, name:str, lookup):
    ret = dict()
    if player_id in players.keys():
        del players[player_id]
        player_order.remove(player_id)
        sysmsg = str()
        if gameon == False or landlord == -1:
            sysmsg = f">>等待区的{player_id}号玩家{name}与服务器连接中断，等待区的其它玩家请重新连接!"
            global_init()
        else:
            if landlord == player_id:
                sysmsg = f">>{player_id}号玩家{name}(地主)与服务器连接中断，此局判农民胜利！"
                global_init()
            else:
                if len(player_order) == 2:
                    sysmsg = f">>{player_id}号玩家{name}(农民)与服务器连接中断，视为弃赛，请地主和剩下的农民继续游戏！"
                elif len(player_order) == 1:
                    sysmsg = f">>{player_id}号玩家{name}(农民)与服务器连接中断，视为弃赛，农民全部弃赛，此局判地主胜利！"
                    global_init()
        for ida in lookup.keys():
            ret[ida] = sysmsg
        return ret
    else:
        for ida in lookup.keys():
            ret[ida] = f">>{player_id}号用户{name}与服务器连接中断了"
        return ret

def logic_client_connect(id:int, lookup):
    ret = dict()
    for ida in lookup.keys():
        ret[ida] = f">>{id}号用户{lookup[id]}连接到了服务器"
    ret[id] = ret[id] + help
    return ret

def logic(id:int, lookup, message:str):#lookup:dict[int,str],returns a dict[int,str]
    global players, player_order, carddeck, waiting, gameon, landlord
    ret = dict()
    cmd = message.split()
    if len(cmd)>0:
        capital = ord(cmd[0][0])
    else:
        ret[id] = "不能输入空指令"
        return ret
    if (not(capital>=65 and capital<=90) and not(capital>=48 and capital<=57)):#首字符不满足A-Z0-9,视为聊天
        for ida in lookup.keys():
            ret[ida] = f">>{lookup[id]}({id}):\"" + message + "\""
        return ret
    if cmd[0]=="WHO":
        ret[id] = str(lookup)
        return ret
    if cmd[0]=="JOIN":
        if gameon:
            ret[id] = "游戏进行中，房间已被占用"
            return ret
        elif id in players.keys():
            ret[id] = "您已在等待区中"
            return ret
        elif waiting < 2:
            players[id] = Game(carddeck[waiting*17:waiting*17+17])
            player_order.append(id)
            waiting += 1
            for idw in players.keys():
                ret[idw] = f">>{id}号玩家{lookup[id]}加入了等待区，还差{3-len(players)}人就可以开始游戏"
            waitinglist = [lookup[idw] for idw in players.keys()]
            ret[id] = f"加入等待成功，目前有"+str(waitinglist)+f"在等待，还差{3-len(players)}人就可以开始游戏"
            return ret
        elif waiting == 2:
            players[id] = Game(carddeck[waiting*17:waiting*17+17])
            player_order.append(id)
            waiting = 0
            gameon = True
            for one_id in players.keys():
                ret[one_id] = f">>人数达到三人，游戏开始，输入命令\"LANDLORD\"抢地主，先抢先得"
            return ret
    #只有玩家可以执行的操作
    if not id in players.keys():
        ret[id] = "抱歉，您不在当前的游戏中，不能进行操作"
        return ret
    if cmd[0]=="LANDLORD":
        if landlord >= 0:
            ret[id] = "已经有人抢到地主了"
            return ret
        else:
            landlord = id
            players[landlord].addcards(carddeck[51:54])
            dizhupai = [players[id].charfor(carddeck[index]) for index in range(51,54)]
            while player_order[0] != landlord:
                    rotate(player_order)
            for one_id in players.keys():
                ret[one_id] = f">>{id}号玩家{lookup[id]}抢到了地主，地主牌是"+str(dizhupai)+f"，按{player_order[0]}->{player_order[1]}->{player_order[2]}号玩家的顺序出牌"
            ret[landlord] = ret[landlord] + "你抢到了地主，请开始出牌，手牌为" + players[landlord].getcards()
            return ret
    if cmd[0]=="PEEK":
        ret[id] = "您的手牌为" + players[id].getcards()
        return ret
    legal_card_name = players[id].K_number.copy()
    legal_card_name.extend(['BlackJoker','RedJoker'])
    if cmd[0] in legal_card_name or cmd[0] == "BUCHU":
        if id != player_order[0]:
            ret[id] = "不是您的出牌回合"
            return ret
        if cmd[0] == "BUCHU":
            descrip = f">>玩家{lookup[id]}({id})不出"
            game_ended = False
        else:
            if players[id].usecards(cmd):
                descrip = f">>玩家{lookup[id]}({id})出了" + str(cmd) + f" ，还剩{len(players[id].data)}张牌"
            else:
                ret[id] = "非法出牌，请重新出牌"
                return ret
            game_ended = (len(players[id].data)==0)
            if game_ended:
                if landlord==id:
                    descrip = descrip + "，地主获胜"
                else:
                    descrip = descrip + "，农民获胜"
        for ida in lookup.keys():
            ret[ida] = ">>已有对局结束了，服务器可用，输入\"JOIN\"指令加入等待区吧"
        for ida in players.keys():
            ret[ida] = descrip
        if game_ended:
            global_init()
        else:
            rotate(player_order)
            ret[player_order[0]] = ret[player_order[0]] + "\n轮到您出牌，手牌为：" + players[player_order[0]].getcards()
        return ret
    else:
        ret[id] = "无法识别的输入格式"
        return ret