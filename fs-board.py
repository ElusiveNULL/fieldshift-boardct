#!/bin/env python3
from os import system


# CLASS DEFINITIONS #
class Operator:
    atk = 4
    max_hp = 5

    def __init__(self, hp, op_id, job, team, reserve, location: int, alive):
        self.hp = hp
        self.op_id = op_id
        self.job = job
        self.team = team
        self.reserve = reserve
        self.location = location
        self.alive = alive

    def take_damage(self, dmg_amount):
        self.hp -= dmg_amount
        if self.hp < 1:
            self.alive = False
            self.reserve = True
            board.contents[self.location].remove(self)


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


class Battlefield:
    def __init__(self, contents, terrain):
        self.contents = contents
        self.terrain = terrain


class Facility:
    def __init__(self, job, allocated, facility_id, facility_aux):
        self.job = job
        self.allocated = allocated
        self.facility_id = facility_id
        self.facility_aux = facility_aux


# PREPARATIONS #
p1 = Player("No name", 1, [], None,
            [Facility("Artillery", 0, 0, 0), Facility("Medbay", 0, 1, 4), Facility("Base", 0, 2, None)])
p2 = Player("No name", 2, [], None,
            [Facility("Artillery", 0, 0, 0), Facility("Medbay", 0, 1, 4), Facility("Base", 0, 2, None)])


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
def switch_reserve_status(op):
    if op.reserve:
        op.reserve = False
        if current_player == p1:
            board.contents[0].append(op)
            current_player.selected_op.location = 0
        else:
            board.contents[9].append(op)
            current_player.selected_op.location = 9
    else:
        op.reserve = True
        board.contents[op.location].remove(op)
        if op == current_player.selected_op:
            for op in current_player.ops:
                if op.alive and not op.reserve:
                    current_player.selected_op = op
                    break


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


current_player = p1
other_player = p2
active_game = True


def check_cooldowns():
    if current_player.skill_delay > 0:
        current_player.skill_delay -= 1
    if current_player.support_delay > 0:
        current_player.support_delay -= current_player.facilities[2].allocated + 1
        if current_player.support_delay < 0:
            current_player.support_delay = 0
    if current_player.facilities[1].facility_aux > 0:  # If medbay heal cooldown has not completed
        # If the medbay's crates + 1 are less than the cooldown
        if current_player.facilities[1].allocated + 1 < current_player.facilities[1].facility_aux:
            # Subtract medbay cooldown by medbay crates + 1
            current_player.facilities[1].facility_aux -= current_player.facilities[1].allocated + 1
            if current_player.facilities[1].facility_aux < 0:
                current_player.facilities[1].facility_aux = 0
        else:
            current_player.facilities[1].facility_aux -= 1
    else:
        heal_amount = 2
        if current_player.facilities[1].allocated > 3:
            heal_amount += current_player.facilities[1].allocated - 3
        for op in current_player.ops:
            if op.reserve and op.hp < 5:
                op.hp += heal_amount
                if op.hp > 5:
                    op.hp = 5


def print_player_info(pname):
    global active_game
    deployed_ops = 0
    print("[Player " + str(pname.player_id) + ": " + pname.name + "]" +
          "\nSkill Cooldown:", end=" ")
    if pname.skill_delay > 0:
        print(str(pname.skill_delay), end="")
    else:
        print("[READY]", end="")
    print("\nSupport Cooldown:", end=" ")
    if pname.support_delay > 0:
        print(str(pname.support_delay))
    else:
        print("[READY]")
    print("Crates: " + str(pname.crates) +
          "\nFacility Crates: " + str(pname.facilities[0].allocated) +
          "-" + str(pname.facilities[1].allocated) +
          "-" + str(pname.facilities[2].allocated) +
          "\nReserve:", end=" ")
    for op in pname.ops:
        if op.alive:
            if op.reserve:
                if op.hp < 5:
                    print(str(pname.ops.index(op)) + "v" + str(op.hp), end=" ")
                else:
                    print(str(pname.ops.index(op)), end=" ")
            else:
                deployed_ops += 1
    if deployed_ops == 0:
        print("")
        system("cls||clear")
        print("Player " + str(pname.player_id)
              + ": Game over - All deployed operators eliminated.\n[PLAYER " +
              str(other_player.player_id) + " VICTORY]\n")
        active_game = False
        return False
    print("\n")
    return True


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


def parse_cmd(cmd):
    global active_game
    global current_player
    global other_player
    cmd_arg = int(cmd[1])
    should_switch = True
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
            other_player.ops[cmd_arg].take_damage(atk_damage)
        case 4:  # RNF - Reinforce
            current_player.crates -= 1
            current_player.facilities[cmd_arg].allocated += 1
        case 5:  # WDR - Withdraw
            current_player.crates += 1
            current_player.facilities[cmd_arg].allocated -= 1
            should_switch = False
        case 6:  # RGP - Regroup
            rgp_target = current_player.ops[cmd_arg]
            switch_reserve_status(rgp_target)
        case 9:  # SPT - Support
            if current_player.facilities[0].auxiliary == 1:
                current_player.support_delay = 5 - current_player.facilities[2].allocated
                current_player.facilities[0].auxiliary = 0
                for op in board.contents[cmd_arg]:
                    if op.team == other_player.player_id:
                        op.take_damage(current_player.facilities[0].allocated)
            else:
                selected_facility = current_player.facilities[cmd_arg]
                match cmd_arg:
                    case 0:
                        selected_facility.auxiliary = 1
                    case 1:
                        for op in current_player.ops:
                            if op.hp < 5 and not op.reserve:
                                op.hp += 2
                                if op.hp > 5:
                                    op.hp = 5
                    case 2:
                        for op in current_player.ops:
                            switch_reserve_status(op)
        case _:
            pass
    check_cooldowns()
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
    if not print_player_info(p1):
        continue
    if not print_player_info(p2):
        continue
    print_board()
