#!/bin/env python3
from os import system


# CLASS DEFINITIONS #
class Operator:
    atk = 4
    max_hp = 5

    def __init__(self, hp: int, op_id: str, job: str, team: int, reserve: bool, location: int, alive: bool):
        self.hp = hp
        self.op_id = op_id
        self.job = job
        self.team = team
        self.reserve = reserve
        self.location = location
        self.alive = alive

    def take_damage(self, dmg_amount: int):
        self.hp -= dmg_amount
        if self.hp < 1:
            self.alive = False
            self.reserve = True
            board.contents[self.location].remove(self)


class Facility:
    def __init__(self, job: str, allocated: int, facility_id: int, facility_aux: int):
        self.job = job
        self.allocated = allocated
        self.facility_id = facility_id
        self.facility_aux = facility_aux


class Player:
    def __init__(self, name: str, player_id: int, ops: list[Operator],
                 selected_op: Operator, facilities: list[Facility], cheated: bool):
        self.crates = 1
        self.skill_delay = 5
        self.support_delay = 5
        self.name = name
        self.player_id = player_id
        self.ops = ops
        self.selected_op = selected_op
        self.facilities = facilities
        self.cheated = cheated


class Battlefield:
    def __init__(self, contents: list[list[Operator]], terrain: list[str]):
        self.contents = contents
        self.terrain = terrain


def create_operators(player_num: int, is_reserve: bool):
    jobs = ["Longwatch", "Technician", "Blade", "Medic", "Specialist"]
    id_list = list(range(10))
    if is_reserve:
        id_list = id_list[4:]
    player_char = '+'
    starting_sector = 0
    if player_num == 2:
        starting_sector = 9
        player_char = '-'
    temp, result = list[str](), list[Operator]()
    for op_id in id_list:
        temp.append(player_char + str(op_id))
    id_list = temp
    result = []
    for i in range(5):
        result.append(Operator(5, id_list[i], jobs[i], player_num, is_reserve, starting_sector, True))
    return result


# PREPARATIONS #
def create_player(player_name: str, player_id: int):
    operators = create_operators(player_id, False)
    operators.extend(create_operators(player_id, True))
    facilities = [Facility("Artillery", 0, 0, 0), Facility("Medbay", 0, 1, 4), Facility("Base", 0, 2, 0)]
    return Player(player_name, player_id, operators, operators[0], facilities, False)


p1 = create_player("No name", 1)
p2 = create_player("No name", 2)
board = Battlefield([], [])


def create_sectors():
    sector_list = ["Ruins", "Grass", "Plain", "Plain", "Mount"]
    board.terrain.extend(sector_list)
    board.terrain.extend(sector_list[::-1])
    for i in range(10):
        board.contents.append(list())


create_sectors()
# First 5 operators are not in reserve
board.contents[0].extend(p1.ops[:5])
board.contents[9].extend(p2.ops[:5])


# SUPPORTING FUNCTIONS #
def switch_reserve_status(operator: Operator, is_support: bool):
    if operator.reserve:
        if not is_support:
            current_player.crates -= 1
        operator.reserve = False
        if current_player == p1:
            board.contents[0].append(operator)
            current_player.selected_op.location = 0
        else:
            board.contents[9].append(operator)
            current_player.selected_op.location = 9
    else:
        if not is_support:
            current_player.crates += 1
        operator.reserve = True
        board.contents[operator.location].remove(operator)
        if operator == current_player.selected_op:
            for op in current_player.ops:
                if op.alive and not op.reserve:
                    current_player.selected_op = op
                    break


def check_range(attacker: Operator, target: Operator, automatic: bool):
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
        if automatic:  # If check_range was executed due to an automatic attack, will not mark out of range as cheating
            return 0
        current_player.cheated = True
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


def print_player_info(player: Player):
    global active_game
    deployed_ops = 0
    print("[Player " + str(player.player_id) + ": " + player.name + "]" +
          "\nSkill Cooldown:", end=" ")
    if player.skill_delay > 0:
        print(str(player.skill_delay), end="")
    else:
        print("[READY]", end="")
    print("\nSupport Cooldown:", end=" ")
    if player.support_delay > 0:
        print(str(player.support_delay))
    else:
        print("[READY]")
    print("Crates: " + str(player.crates) +
          "\nFacility Crates: " + str(player.facilities[0].allocated) +
          "-" + str(player.facilities[1].allocated) +
          "-" + str(player.facilities[2].allocated) +
          "\nReserve:", end=" ")
    for op in player.ops:
        if op.alive:
            if op.reserve:
                if op.hp < 5:
                    print(str(player.ops.index(op)) + "v" + str(op.hp), end=" ")
                else:
                    print(str(player.ops.index(op)), end=" ")
            else:
                deployed_ops += 1
    if deployed_ops == 0:
        print("")
        print("Player " + str(player.player_id)
              + ": Game over - All deployed operators eliminated.\n[PLAYER " +
              str(other_player.player_id) + " VICTORY]\n")
        input("Press Enter to continue...")
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
    current_player.cheated = False
    cmd_arg = int(cmd[1])
    should_switch = True
    if current_player == p1:
        other_player = p2
    else:
        other_player = p1
    match int(cmd[0]):
        case 0:  # AUX - Auxiliary
            match cmd_arg:
                case 3:  # Concede
                    print("Player " + str(current_player.player_id)
                          + ": Concede\n[PLAYER " + str(
                        other_player.player_id) + " VICTORY]")
                    input("Press Enter to continue...")
                    return False
                case 6:  # Dispute
                    if other_player.cheated:
                        print("Player " + str(other_player.player_id)
                              + ": Game over - Called out for rule breakage\n[PLAYER " + str(
                            other_player.player_id) + " VICTORY]")
                        input("Press Enter to continue...")
                        return False
                case 8:
                    system("clear||cls")
                    print("Player " + str(current_player.player_id) + ": Request draw")
                    if input("Player " + str(other_player.player_id) + " response: ") == "01":
                        system("clear||cls")
                        print_player_info(p1)
                        print_player_info(p2)
                        print_board()
                        print("Game concluded: Draw by mutual agreement")
                        input("Press Enter to continue...")
                        return False
                    should_switch = False

        case 1:  # SWC - Switch
            current_player.selected_op = current_player.ops[cmd_arg]
            should_switch = False

        case 2:  # MOV - Move
            board.contents[current_player.selected_op.location].remove(current_player.selected_op)
            board.contents[cmd_arg].append(current_player.selected_op)
            current_player.selected_op.location = cmd_arg

        case 3:  # HIT - Attack
            other_player.ops[cmd_arg].take_damage(check_range(
                current_player.selected_op, other_player.ops[cmd_arg], False))

        case 4:  # RNF - Reinforce
            current_player.crates -= 1
            current_player.facilities[cmd_arg].allocated += 1

        case 5:  # WDR - Withdraw
            current_player.crates += 1
            current_player.facilities[cmd_arg].allocated -= 1
            should_switch = False

        case 6:  # RGP - Regroup
            rgp_target = current_player.ops[cmd_arg]
            switch_reserve_status(rgp_target, False)

        case 9:  # SPT - Support
            if current_player.facilities[0].facility_aux == 1:
                current_player.support_delay = 5 - current_player.facilities[2].allocated
                current_player.facilities[0].facility_aux = 0
                for op in board.contents[cmd_arg]:
                    if op.team == other_player.player_id:
                        op.take_damage(current_player.facilities[0].allocated)
            else:
                selected_facility = current_player.facilities[cmd_arg]
                match cmd_arg:
                    case 0:
                        selected_facility.facility_aux = 1
                    case 1:
                        for op in current_player.ops:
                            if op.hp < 5 and not op.reserve:
                                op.hp += 2
                                if op.hp > 5:
                                    op.hp = 5
                    case 2:
                        for op in current_player.ops:
                            switch_reserve_status(op, True)
                    case _:
                        should_switch = False

        case _:
            should_switch = False
    check_cooldowns()
    if should_switch:
        if current_player == p1:
            current_player = p2
        else:
            current_player = p1
    return True


# MAIN #
system("clear||cls")
p1.name = input("Enter name of Player 1: ")
p2.name = input("Enter name of Player 2: ")
system("clear||cls")
print_player_info(p1)
print_player_info(p2)
print_board()
while active_game:
    if not parse_cmd((input("Player " + str(current_player.player_id) +
                            " (" + current_player.selected_op.op_id + "): "))):
        break
    # Print updated info
    system("clear||cls")
    if not print_player_info(p1):
        continue
    if not print_player_info(p2):
        continue
    print_board()
