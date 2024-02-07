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
    def __init__(self,hp,opid,job,team,reserve,location,alive):
        self.hp = hp
        self.opid = opid
        self.job = job
        self.team = team
        self.reserve = reserve
        self.location = location
        self.alive = alive

class Battlefield:
    def __init__(self,contents):
        self.contents = contents

class Facilities:
    def __init__(self,job,crates,facilityid):
        self.job = job
        self.crates = crates
        self.facilityid = facilityid

### PREPARATIONS ###
p1 = Player("No name",1,[],None)
p2 = Player("No name",2,[],None)
def createOperators(playernum, isreserve: bool):
    jobs = ["Longwatch","Technician","Blade","Medic","Specialist"]
    idlist = list(range(10))
    if isreserve:
        idlist = idlist[4:]
    playerchar = '+'
    startingsector = 0
    if (playernum == 2):
        startingsector = 9
        playerchar = '-'
    temp,result = [], []
    for i in idlist:
        temp.append(playerchar + str(i))
    idlist = temp
    result = []
    for i in range(5):
        result.append(Operator(5,idlist[i],jobs[i],playernum,isreserve,startingsector,True))
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

p1.selectedop = p1.ops[0]
p2.selectedop = p2.ops[0]

### SUPPORTING FUNCTIONS ###
def printPlayerStats(pname):
    print("[Player " + str(pname.playerid) + ": " + pname.name + "]" + \
         "\nSkill Cooldown: " + str(pname.skilldelay) + \
         "\nSupport Cooldown: " + str(pname.supportdelay) + \
         "\nCrates: " + str(pname.crates) + \
         "\nReserve:",end=" ")
    for op in pname.ops:
       if op.reserve and op.alive:
           print(str(pname.ops.index(op)),end=" ")
    print("\n")

def printBoard():
    for i in range(10):
        print("Sector " + str(i) + ":",end=" ")
        for op in board.contents[i]:
            print(op.opid,end="")
            if (op.hp < 5):
                print("v" + str(op.hp),end="")
            print(end=" ")
        print("")
    print("\n")

currentplayer = p1

def parsecmd(cmd):
    cmdarg = int(cmd[1])
    shouldswitch = True
    global currentplayer
    if currentplayer == p1:
        otherplayer = p2
    else:
        otherplayer = p1
    match int(cmd[0]):
        case 0:
            shouldswitch = False
        case 1:
            currentplayer.selectedop = currentplayer.ops[cmdarg]
            shouldswitch = False
        case 2:
            board.contents[currentplayer.selectedop.location].remove(currentplayer.selectedop)
            board.contents[cmdarg].append(currentplayer.selectedop)
            currentplayer.selectedop.location = cmdarg
        case 3:
            otherplayer.ops[cmdarg].hp -= 3
            if (otherplayer.ops[cmdarg].hp < 1):
                otherplayer.ops[cmdarg].alive = False
                otherplayer.ops[cmdarg].reserve = True
                board.contents[otherplayer.ops[cmdarg].location].remove(otherplayer.ops[cmdarg])
        case _:
            pass
    if (shouldswitch):
        if (currentplayer == p1):
            currentplayer = p2
        else:
            currentplayer = p1

### MAIN ###
activegame = True
p1.name = input("Enter name of Player 1: ")
p2.name = input("Enter name of Player 2: ")
print("[COMMENCE GAME]")
while activegame:
    parsecmd((input("Player " + str(currentplayer.playerid) + ": ")))
    # Print updated info
    print(chr(27) + "[2J")
    printPlayerStats(p1)   
    printPlayerStats(p2)
    printBoard()