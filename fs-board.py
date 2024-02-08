# IMPORTS #
from os import system


# CLASS DEFINITIONS #
class Player:
    def __init__(self, name, player_id, ops, selected_op, facilities):
        self.crates = 1
        self.skill_delay = 5
        self.support_delay = 5
        self.name = name
        self.player_id = player_id
        self.ops = ops
        self.selected_op = selected_op
        self.facilities = facilities


class Operator:
    atk = 4
    max_hp = 5

    def __init__(self, hp, op_id, job, team, reserve, location, alive):
        self.hp = hp
        self.op_id = op_id
        self.job = job
        self.team = team
        self.reserve = reserve
        self.location = location
        self.alive = alive


class Battlefield:
    def __init__(self, contents, terrain):
        self.contents = contents
        self.terrain = terrain


class Facility:
    def __init__(self, job, crates, facility_id):
        self.job = job
        self.crates = crates
        self.facility_id = facility_id


# PREPARATIONS #
p1 = Player("No name", 1, [], None, [Facility("Artillery", 0, 0), Facility("Medbay", 0, 1), Facility("Base", 0, 2)])
p2 = Player("No name", 2, [], None, [Facility("Artillery", 0, 0), Facility("Medbay", 0, 1), Facility("Base", 0, 2)])


def create_operators(player_num, is_reserve: bool):
    jobs = ["Longwatch", "Technician", "Blade", "Medic", "Specialist"]
    id_list = list(range(10))
    if is_reserve:
        id_list = id_list[4:]
    player_char = '+'
    starting_sector = 0
    if player_num == 2:
        starting_sector = 9
        player_char = '-'
    temp, result = [], []
    for op_id in id_list:
        temp.append(player_char + str(op_id))
    id_list = temp
    result = []
    for i in range(5):
        result.append(Operator(5, id_list[i], jobs[i], player_num, is_reserve, starting_sector, True))
    return result


p1.ops = create_operators(1, False)
p2.ops = create_operators(2, False)

board = Battlefield([], [])


def create_sectors():
    sector_list = ["Ruins", "Grass", "Plain", "Plain", "Mount"]
    board.terrain.extend(sector_list)
    board.terrain.extend(sector_list[::-1])
    for i in range(10):
        board.contents.append(list())


create_sectors()
board.contents[0].extend(p1.ops)
board.contents[9].extend(p2.ops)
p1.ops.extend(create_operators(1, True))
p2.ops.extend(create_operators(2, True))

p1.selected_op = p1.ops[0]
p2.selected_op = p2.ops[0]


# SUPPORTING FUNCTIONS #
def check_range(attacker, target):
    net_range = 3
    net_damage = attacker.atk
    if attacker.job == "Longwatch":
        net_range = 5
    match target.location:
        case 0 | 9:
            net_range -= 2
            net_damage -= 2
        case 1 | 8:
            net_range -= 1
        case 4 | 5:
            net_damage += 1
    if attacker.location == 4 or attacker.location == 5:
        net_damage += 1
    if attacker.job == "Blade":
        net_range = 0
    if net_range < abs(attacker.location - target.location):
        return -1
    return net_damage


def print_player_info(pname):
    print("[Player " + str(pname.player_id) + ": " + pname.name + "]" +
          "\nSkill Cooldown: " + str(pname.skill_delay) +
          "\nSupport Cooldown: " + str(pname.support_delay) +
          "\nCrates: " + str(pname.crates) +
          "\nFacility Crates: " + str(pname.facilities[0].crates) +
          "-" + str(pname.facilities[1].crates) +
          "-" + str(pname.facilities[2].crates) +
          "\nReserve:", end=" ")
    for op in pname.ops:
        if op.reserve and op.alive:
            print(str(pname.ops.index(op)), end=" ")
    print("\n")


def print_board():
    for i in range(10):
        print(board.terrain[i] + " Sector " + str(i) + ":", end=" ")
        for op in board.contents[i]:
            print(op.op_id, end="")
            if op.hp < 5:
                print("v" + str(op.hp), end="")
            print(end=" ")
        print("")
    print("\n")


current_player = p1
active_game = True


def parse_cmd(cmd):
    global active_game
    cmd_arg = int(cmd[1])
    should_switch = True
    global current_player
    if current_player == p1:
        other_player = p2
    else:
        other_player = p1
    match int(cmd[0]):
        case 0:  # AUX - Auxiliary
            should_switch = False
        case 1:  # SWC - Switch
            current_player.selected_op = current_player.ops[cmd_arg]
            should_switch = False
        case 2:  # MOV - Move
            board.contents[current_player.selected_op.location].remove(current_player.selected_op)
            board.contents[cmd_arg].append(current_player.selected_op)
            current_player.selected_op.location = cmd_arg
        case 3:  # HIT - Attack
            atk_damage = check_range(current_player.selected_op, other_player.ops[cmd_arg])
            if atk_damage == -1:
                system("cls||clear")
                print("Player " + str(current_player.player_id)
                      + ": Illegal action - Insufficient range.\n[PLAYER " + str(other_player.player_id) + " VICTORY]")
                return False
            other_player.ops[cmd_arg].hp -= atk_damage
            if other_player.ops[cmd_arg].hp < 1:
                other_player.ops[cmd_arg].alive = False
                other_player.ops[cmd_arg].reserve = True
                board.contents[other_player.ops[cmd_arg].location].remove(other_player.ops[cmd_arg])
        case 4:  # RNF - Reinforce
            current_player.crates -= 1
            current_player.facilities[cmd_arg].crates += 1
        case 5:  # RLC - Reallocate
            current_player.crates += 1
            current_player.facilities[cmd_arg].crates -= 1
            should_switch = False
        case 6:  # RGP - Regroup
            if current_player.ops[cmd_arg].reserve:
                current_player.ops[cmd_arg].reserve = False
                if current_player == p1:
                    board.contents[0].append(current_player.ops[cmd_arg])
                    current_player.selected_op.location = 0
                else:
                    board.contents[9].append(current_player.ops[cmd_arg])
                    current_player.selected_op.location = 9
            else:
                current_player.ops[cmd_arg].reserve = True
                board.contents[current_player.ops[cmd_arg].location].remove(current_player.ops[cmd_arg])
        case _:
            pass
    if should_switch:
        if current_player == p1:
            current_player = p2
        else:
            current_player = p1
    return True


# MAIN #
system("cls||clear")
p1.name = input("Enter name of Player 1: ")
p2.name = input("Enter name of Player 2: ")
system("cls||clear")
print_player_info(p1)
print_player_info(p2)
print_board()
while active_game:
    if not parse_cmd((input("Player " + str(current_player.player_id) +
                            " (" + current_player.selected_op.op_id + "): "))):
        break
    # Print updated info
    system("cls||clear")
    print_player_info(p1)
    print_player_info(p2)
    print_board()
