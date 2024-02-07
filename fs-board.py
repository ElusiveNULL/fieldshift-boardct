### CLASS DEFINITIONS ###
class Player:
    def __init__(self,name,playerid,ops,selectedop):
        self.crates = 1
        self.skilldelay = 5
        self.supportdelay = 5
        self.name = name
        self.ops = []
        self.playerid = playerid
        self.selectedop = selectedop

class Operator:
    atk = 4
    maxhp = 5
    def __init__(self,hp,opid,job,team,reserve):
        self.hp = hp
        self.opid = opid
        self.job = job
        self.team = team
        self.reserve = reserve

class Battlefield:
    def __init__(self,contents):
        self.contents = contents

class Facilities:
    def __init__(self,job,crates,facilityid):
        self.job = job
        self.crates = crates
        self.facilityid = facilityid

### PREPARATIONS ###
p1 = Player("No name",1,[])
p2 = Player("No name",2,[])
def createOperators(playernum, isreserve: bool):
    jobs = ["Longwatch","Technician","Blade","Medic","Specialist"]
    idlist = list(range(10))
    if isreserve:
        idlist = idlist[4:]
    playerchar = '+'
    if (playernum == 2):
        playerchar = '-'
    temp,result = [], []
    for i in idlist:
        temp.append(playerchar + str(i))
    idlist = temp
    result = []
    for i in range(5):
        result.append(Operator(5,idlist[i],jobs[i],playernum,isreserve))
    return result

p1.ops = createOperators(1,False)
p2.ops = createOperators(2,False)

board = Battlefield(list())
for i in range(10):
    board.contents.append(list())
board.contents[0].extend(p1.ops)
board.contents[9].extend(p2.ops)
p1.ops.extend(createOperators(1,True))
p2.ops.extend(createOperators(2,True))

### SUPPORTING FUNCTIONS ###
def printPlayerStats(pname):
    print("[Player " + str(pname.playerid) + ": " + pname.name + "]" + \
         "\nSkill Cooldown: " + str(pname.skilldelay) + \
         "\nSupport Cooldown: " + str(pname.supportdelay) + \
         "\nCrates: " + str(pname.crates) + \
         "\nReserve:",end=" ")
    for op in pname.ops:
       if op.reserve == True:
           print(str(pname.ops.index(op)),end=" ")
    print("\n")

def printBoard():
    for i in range(10):
        print("Sector " + str(i) + ":",end=" ")
        for op in board.contents[i]:
            print(op.opid,end=" ")
        print("")
    print("\n")

def parsecmd(cmd):
    match cmd[0]:
        case 0:
            pass
        case 1:
            pass

### MAIN ###
activegame = True
p1.name = input("Enter name of Player 1: ")
p2.name = input("Enter name of Player 2: ")
print("[COMMENCE GAME]")
currentplayer = p1
while activegame:
    command = int(input("Player " + str(currentplayer.playerid) + ": "))
    # Print updated info
    print(chr(27) + "[2J")
    printPlayerStats(p1)   
    printPlayerStats(p2)
    printBoard()
    if (currentplayer == p2):
        currentplayer = p2
    else:
        currentplayer = p1