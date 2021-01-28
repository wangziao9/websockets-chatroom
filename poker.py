import random

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
        elif(x==53):
            return '小王'
        elif(x==54):
            return '大王'
    def getcards(self) -> str:
        self.data.sort()
        ret = ""
        for i,card in enumerate(self.data):
            ret = ret + str(i) + ":" + self.charfor(card) + " "
        return ret
    def usecards(self, coll) -> str:#coll:List[int]
        coll.sort()
        cardout = []
        print("coll:")
        print(str(coll))
        while len(coll) > 0:
            index = coll.pop()
            print("index:%d",index)
            if index >= 0 and index < len(self.data):
                print("good index:%d",index)
                cardout.append(self.data[index])
                del self.data[index]
        cardout.reverse()
        for index,card in enumerate(cardout):
            cardout[index] = self.charfor(card)
        return str(cardout)

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

def logic(id:int, ids, message:str):#ids:List[int],returns a dict[int,str]
    global players, player_order, carddeck, waiting, gameon, landlord
    ret = dict()
    cmd = message.split()
    if cmd[0]=="CHAT":
        for ida in ids:
            ret[ida] = f">>{id}号玩家:\"" + message[4:] + "\""
        return ret
    if cmd[0]=="JOIN":
        if gameon:
            ret[id] = "游戏进行中，房间已被占用"
            return ret
        elif waiting < 2:
            players[id] = Game(carddeck[waiting*17:waiting*17+17])
            player_order.append(id)
            waiting += 1
            ret[id] = f"加入等待成功，目前有{len(players)}人等待"
            return ret
        elif waiting == 2:
            players[id] = Game(carddeck[waiting*17:waiting*17+17])
            player_order.append(id)
            waiting = 0
            gameon = True
            for one_id in players.keys():
                ret[one_id] = f">>人数达到三人，游戏开始，抢地主动作要快"
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
            while player_order[0] != landlord:
                    rotate(player_order)
            for one_id in players.keys():
                ret[one_id] = f">>{id}号玩家抢到了地主，按{player_order[0]},{player_order[1]},{player_order[2]}的顺序出牌"
            return ret
    if cmd[0]=="PEEK":
        ret[id] = "您的手牌为" + players[id].getcards()
        return ret
    if cmd[0]==">":
        if id != player_order[0]:
            ret[id] = "不是您的出牌回合"
            return ret
        outcards = list()
        for i in range(1,len(cmd)):
            card_pos = -1
            try:
                card_pos = int(cmd[i])
                outcards.append(card_pos)
            except ValueError:
                ret[id] = "非数字输入，请重新选牌"
                return ret
        print("Outcards:")
        print(str(outcards))
        descrip = f">>玩家{id}出了" + players[id].usecards(outcards) + f" ；他还有{len(players[id].data)}张牌"
        game_ended = (len(players[id].data)==0)
        if game_ended:
            if landlord==id:
                descrip = descrip + "，地主获胜"
            else:
                descrip = descrip + "，农民获胜"
        for ida in players.keys():
            ret[ida] = descrip
        if game_ended:
            global_init()
        else:
            rotate(player_order)
        return ret
    else:
        ret[id] = "无法识别的输入格式"
        return ret