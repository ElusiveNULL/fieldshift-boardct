### CLASS DEFINITIONS ###
class Player:
    def __init__(self,name,ops):
        self.crates = 1
        self.skilldelay = 5
        self.supportdelay = 5
        self.name = name
        self.ops = []

class Operator:
    atk = 4
    maxhp = 5

    def __init__(self,hp,job,playerid,reserve):
        self.hp = hp
        self.job = job
        self.playerid = playerid
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
p1 = Player("No name")
p2 = Player("No name")
def createOperators(playernum, isreserve: bool):
    jobs = ["Longwatch","Technician","Blade","Medic","Specialist"]
    result = []
    for job in jobs:
        result.append(Operator(5,job,playernum,isreserve))
    return result

p1ops = createOperators(1,False)
p2ops = createOperators(2,False)

bf1 = Battlefield(list())
for i in range(10):
    bf1.contents.append(list())
bf1.contents[0].extend(p1ops)
bf1.contents[9].extend(p2ops)
p1ops.extend(createOperators(1,True))
p2ops.extend(createOperators(2,True))

### MAIN ###
activegame = True
p1.name = input("Player 1 name: ")
p2.name = input("Player 2 name: ")
currentplayer = 1
while activegame:
   cmd = int(input("Player " + currentplayer + ": "))
   # Print board
   print("Player 1: " + p1.name +
         "\nCrates: " + p1.crates +
         "\nSkill Cooldown: " + p1.skilldelay +
         "\nSupport Cooldown: " + p1.supportdelay +
         "\nReserve: ")