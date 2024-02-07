### IMPORTS ###
from os import system
### CLASS DEFINITIONS ###
class Player:
    def __init__(self,name,playerid,ops,selectedop,facilities):
        self.crates = 1
        self.skilldelay = 5
        self.supportdelay = 5
        self.name = name
        self.ops = []
        self.playerid = playerid
        self.selectedop = selectedop
        self.facilities = facilities

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
    def __init__(self,contents,terrain):
        self.contents = contents
        self.terrain = terrain

class Facility:
    def __init__(self,job,crates,facilityid):
        self.job = job
        self.crates = crates
        self.facilityid = facilityid

### PREPARATIONS ###
p1 = Player("No name",1,[],None,[Facility("Artillery",0,0),Facility("Medbay",0,1),Facility("Base",0,2)])
p2 = Player("No name",2,[],None,[Facility("Artillery",0,0),Facility("Medbay",0,1),Facility("Base",0,2)])
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

board = Battlefield([],[])
def createSectors():
    sectorlist = ["Ruins","Grass","Plain","Plain","Mount"]
    board.terrain.extend(sectorlist)
    board.terrain.extend(sectorlist[::-1])
createSectors()

for i in range(10):
    board.contents.append(list())
board.contents[0].extend(p1.ops)
board.contents[9].extend(p2.ops)
p1.ops.extend(createOperators(1,True))
p2.ops.extend(createOperators(2,True))

p1.selectedop = p1.ops[0]
p2.selectedop = p2.ops[0]

### SUPPORTING FUNCTIONS ###
def checkRange(attacker, target):
    effectiveRange = 3
    effectiveDamage = attacker.atk
    if attacker.job == "Longwatch":
        effectiveRange = 5
    match target.location:
        case 0 | 9:
            effectiveRange -= 2
            effectiveDamage -= 2
        case 1 | 8:
            effectiveRange -= 1
        case 4 | 5:
            effectiveDamage += 1
    if attacker.location == 4 or attacker.location == 5:
        effectiveDamage += 1
    if attacker.job == "Blade":
        effectiveRange = 0
    if effectiveRange < abs(attacker.location - target.location):
        return -1
    return effectiveDamage

def printPlayerStats(pname):
    print("[Player " + str(pname.playerid) + ": " + pname.name + "]" + \
         "\nSkill Cooldown: " + str(pname.skilldelay) + \
         "\nSupport Cooldown: " + str(pname.supportdelay) + \
         "\nCrates: " + str(pname.crates) + \
         "\nFacility Crates: " + str(pname.facilities[0].crates) + \
         "-" + str(pname.facilities[1].crates) + \
         "-" + str(pname.facilities[2].crates) + \
         "\nReserve:",end=" ")
    for op in pname.ops:
       if op.reserve and op.alive:
           print(str(pname.ops.index(op)),end=" ")
    print("\n")

def printBoard():
    for i in range(10):
        print(board.terrain[i] + " Sector " + str(i) + ":",end=" ")
        for op in board.contents[i]:
            print(op.opid,end="")
            if (op.hp < 5):
                print("v" + str(op.hp),end="")
            print(end=" ")
        print("")
    print("\n")

currentplayer = p1

activegame = True
def parsecmd(cmd):
    global activegame 
    cmdarg = int(cmd[1])
    shouldswitch = True
    global currentplayer
    if currentplayer == p1:
        otherplayer = p2
    else:
        otherplayer = p1
    match int(cmd[0]):
        case 0: # AUX - Auxiliary
            shouldswitch = False
        case 1: # SWC - Switch
            currentplayer.selectedop = currentplayer.ops[cmdarg]
            shouldswitch = False
        case 2: # MOV - Move
            board.contents[currentplayer.selectedop.location].remove(currentplayer.selectedop)
            board.contents[cmdarg].append(currentplayer.selectedop)
            currentplayer.selectedop.location = cmdarg
        case 3: # HIT - Attack
            atkdamage = checkRange(currentplayer.selectedop,otherplayer.ops[cmdarg])
            if atkdamage == -1:
                system("cls||clear")
                print("Player " + str(currentplayer.playerid) \
                      + ": Illegal action - Insufficient range.\n[PLAYER " + str(otherplayer.playerid) + " VICTORY]")
                return False
            otherplayer.ops[cmdarg].hp -= atkdamage
            if (otherplayer.ops[cmdarg].hp < 1):
                otherplayer.ops[cmdarg].alive = False
                otherplayer.ops[cmdarg].reserve = True
                board.contents[otherplayer.ops[cmdarg].location].remove(otherplayer.ops[cmdarg])
        case 4: # RNF - Reinforce
            currentplayer.crates -= 1
            currentplayer.facilities[cmdarg].crates += 1
        case 5: # RLC - Reallocate
            currentplayer.crates += 1
            currentplayer.facilities[cmdarg].crates -= 1
            shouldswitch = False
        case 6: # RGP - Regroup
            if currentplayer.ops[cmdarg].reserve:
                currentplayer.ops[cmdarg].reserve = False
                if currentplayer == p1:
                    board.contents[0].append(currentplayer.ops[cmdarg])
                    currentplayer.selectedop.location = 0
                else:
                    board.contents[9].append(currentplayer.ops[cmdarg])
                    currentplayer.selectedop.location = 9
            else:
                currentplayer.ops[cmdarg].reserve = True
                board.contents[currentplayer.ops[cmdarg].location].remove(currentplayer.ops[cmdarg])
        case _:
            pass
    if (shouldswitch):
        if (currentplayer == p1):
            currentplayer = p2
        else:
            currentplayer = p1
    return True

### MAIN ###
system("cls||clear")
p1.name = input("Enter name of Player 1: ")
p2.name = input("Enter name of Player 2: ")
system("cls||clear")
printPlayerStats(p1)   
printPlayerStats(p2)
printBoard()
while activegame:
    if not parsecmd((input("Player " + str(currentplayer.playerid) + " (" + currentplayer.selectedop.opid + "): "))):
        break
    # Print updated info
    system("cls||clear")
    printPlayerStats(p1)
    printPlayerStats(p2)
    printBoard()