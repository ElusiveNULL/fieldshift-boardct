#!/bin/env python3
import os
import sys
from typing import TextIO


if os.name == "nt":
    # Enable ANSI in Windows
    os.system("")


# CLASS DEFINITIONS #
class Game:
    def __init__(self, is_in_playback: bool, input_stream: TextIO):
        self.is_finished = False
        self.game_log = ""

        self.is_in_playback = is_in_playback
        self.input_stream = input_stream

        p1 = create_player("No name", 1)
        p2 = create_player("No name", 2)
        board = Battlefield([], [])
        create_sectors(board)
        # First 5 operators are not in reserve
        board.contents[0].extend(p1.ops[:5])
        board.contents[9].extend(p2.ops[:5])

        self.p1 = p1
        self.p2 = p2
        self.board = board
        self.current_player = p1
        self.other_player = p2

        self.overwatch_state = False
        self.overwatch_operator = p1.ops[5]


class Operator:
    atk = 3
    max_hp = 5

    def __init__(self, hp: int, op_id: str, team: int, reserve: bool, location: int, alive: bool, skill_active: int):
        self.hp = hp
        self.op_id = op_id
        self.team = team
        self.reserve = reserve
        self.location = location
        self.alive = alive
        self.skill_active = skill_active

    def take_damage(self, dmg_amount: int):
        self.hp -= dmg_amount
        if self.hp < 1:
            self.alive = False
            self.reserve = True
            self.skill_active = 0
            current_game.board.contents[self.location].remove(self)
            for op in current_game.current_player.ops:
                if op.alive and not op.reserve:
                    current_game.current_player.selected_op = op
                    break


class Facility:
    def __init__(self, job: str, allocated: int, facility_id: int, facility_aux: int):
        self.job = job
        self.allocated = allocated
        self.facility_id = facility_id
        self.facility_aux = facility_aux


class Player:
    def __init__(self, name: str, player_id: int, ops: list[Operator],
                 selected_op: Operator, artillery_facility: Facility, medbay_facility: Facility,
                 command_center_facility: Facility, cheated: bool):
        self.crates = 1
        self.skill_delay = 5
        self.support_delay = 5
        self.name = name
        self.player_id = player_id
        self.ops = ops
        self.selected_op = selected_op
        self.artillery = artillery_facility
        self.medbay = medbay_facility
        self.command_center = command_center_facility
        self.cheated = cheated

    def get_facility_by_index(self, index: int):
        if index > 2:
            return self.artillery
        return [self.artillery, self.medbay, self.command_center][index]


class Battlefield:
    def __init__(self, contents: list[list[Operator]], terrain: list[str]):
        self.contents = contents
        self.terrain = terrain


def create_operators(player_num: int, is_reserve: bool):
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
        result.append(Operator(5, id_list[i], player_num, is_reserve, starting_sector, True, False))
    return result


# PREPARATIONS #
def create_player(player_name: str, player_id: int):
    operators = create_operators(player_id, False)
    operators.extend(create_operators(player_id, True))
    # Overwatch operator assigned to first operator not on the field to avoid the variable ever being empty
    return Player(player_name, player_id, operators, operators[0], Facility("Artillery", 0, 0, 0),
                  Facility("Medbay", 0, 1, 4), Facility("Base", 0, 2, 0), False)


def create_sectors(board: Battlefield):
    sector_list = ["Ruins", "Grass", "Plain", "Plain", "Mount"]
    board.terrain.extend(sector_list)
    board.terrain.extend(sector_list[::-1])
    for i in range(10):
        board.contents.append(list())


# Resume game from argument
if len(sys.argv) > 1:
    current_game = Game(True, open(sys.argv[1]))
else:
    current_game = Game(False, sys.stdin)


# SUPPORTING FUNCTIONS #
def clear_terminal():
    print("\x1b[2J\x1b[3J\x1b[H", end="")


def read_command_input(prompt: str):
    line = ""
    if current_game.is_in_playback:
        line = current_game.input_stream.readline().rstrip()
        # May need to change this for different rulesets
        if len(line) >= 2:
            return line
        else:
            current_game.is_in_playback = False
            current_game.input_stream = sys.stdin

    print(prompt, end=line, flush=True)
    line += current_game.input_stream.readline().rstrip()
    return line


def read_line_input(prompt: str):
    line = ""
    if current_game.is_in_playback:
        line = current_game.input_stream.readline()
        if line.endswith("\n"):
            return line.rstrip()
        else:
            current_game.is_in_playback = False
            current_game.input_stream = sys.stdin

    print(prompt, end=line, flush=True)
    line += current_game.input_stream.readline().rstrip()
    return line


def switch_reserve_status(operator: Operator, is_support: bool):
    if operator.reserve:
        if not is_support:
            current_game.current_player.crates -= 1
        operator.reserve = False
        if current_game.current_player == current_game.p1:
            current_game.board.contents[0].append(operator)
            current_game.current_player.selected_op.location = 0
        else:
            current_game.board.contents[9].append(operator)
            current_game.current_player.selected_op.location = 9
    else:
        if not is_support:
            current_game.current_player.crates += 1
        operator.reserve = True
        current_game.board.contents[operator.location].remove(operator)
        if operator == current_game.current_player.selected_op:
            for op in current_game.current_player.ops:
                if op.alive and not op.reserve:
                    current_game.current_player.selected_op = op
                    break


def check_range(attacker: Operator, target: Operator, automatic: bool, assassinate: bool):
    net_range = 3
    net_damage = attacker.atk
    if attacker.op_id[1] == ("0" or "5"):
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
    if assassinate:
        net_damage += 2
        net_range = 9
    elif attacker.op_id[1] == ("1" or "6"):
        net_range = 0
    if net_range < abs(attacker.location - target.location):
        if automatic:
            # If check_range was executed due to an automatic attack, will not mark out of range as cheating
            return 0
        current_game.current_player.cheated = True
    return net_damage


def check_cooldowns():
    if current_game.current_player.skill_delay > 0:
        current_game.current_player.skill_delay -= 1
    if current_game.current_player.support_delay > 0:
        current_game.current_player.support_delay -= current_game.current_player.command_center.allocated + 1
        if current_game.current_player.support_delay < 0:
            current_game.current_player.support_delay = 0
    if current_game.current_player.medbay.facility_aux > 0:  # If medbay heal cooldown has not completed
        # If the medbay's crates + 1 are less than the cooldown
        if current_game.current_player.medbay.allocated + 1 < current_game.current_player.medbay.facility_aux:
            # Subtract medbay cooldown by medbay crates + 1
            current_game.current_player.medbay.facility_aux -= current_game.current_player.medbay.allocated + 1
            if current_game.current_player.medbay.facility_aux < 0:
                current_game.current_player.medbay.facility_aux = 0
        else:
            current_game.current_player.medbay.facility_aux -= 1
    else:
        heal_amount = 2
        if current_game.current_player.medbay.allocated > 3:
            heal_amount += current_game.current_player.medbay.allocated - 3
        for op in current_game.current_player.ops:
            if op.reserve and op.hp < 5:
                op.hp += heal_amount
                if op.hp > 5:
                    op.hp = 5


def check_overwatch():
    operator = current_game.current_player.ops[0]
    if current_game.other_player.ops[0].skill_active == 1:
        operator = current_game.other_player.ops[0]
    elif current_game.other_player.ops[5].skill_active == 1:
        operator = current_game.other_player.ops[5]
    if operator.team == current_game.other_player.player_id:
        current_game.current_player.selected_op.take_damage(5)
        operator.skill_active = 0
    if current_game.overwatch_state and current_game.overwatch_operator.team == current_game.other_player.player_id:
        attack_check = check_range(
            current_game.overwatch_operator, current_game.current_player.selected_op, True, False
        )
        if (not current_game.overwatch_operator.reserve and current_game.overwatch_operator.alive) and \
                attack_check > 0:
            current_game.current_player.selected_op.take_damage(attack_check)
            current_game.overwatch_state = False
            for operator in current_game.other_player.ops:
                if operator.reserve or not operator.alive:
                    current_game.overwatch_operator = operator


def print_player_info(player: Player):
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
          "\nFacility Crates: " + str(player.artillery.allocated) +
          "-" + str(player.medbay.allocated) +
          "-" + str(player.command_center.allocated) +
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
        print("\nPlayer " + str(player.player_id)
              + ": Game over - All deployed operators eliminated.\n[PLAYER " +
              str(current_game.other_player.player_id) + " VICTORY]\n")
        input("Press Enter to continue...")
        return False
    print("\n")
    return True


def print_board():
    for i in range(10):
        print(current_game.board.terrain[i] + " Sector " + str(i) + ":", end=" ")
        for op in current_game.board.contents[i]:
            print(op.op_id, end="")
            if op.hp < 5:
                print("v" + str(op.hp), end="")
            print(end="")
            if current_game.overwatch_state and op == current_game.overwatch_operator:
                print("W", end="")
            if op.skill_active == 1:
                print("S", end="")
            elif op.skill_active > 1:
                print("S" + str(op.skill_active), end="")
            print("", end=" ")
        print("")
    print("\n")


def validate_command(command: str):
    # May need to update this for different rulesets in the future
    return len(command) == 2 and command.isdecimal()


def parse_command(command):
    global current_game
    if not command == "02" and not command == "03":
        current_game.game_log += command + "\n"
    current_game.current_player.cheated = False
    cmd_arg = int(command[1])
    should_switch = True
    if current_game.current_player == current_game.p1:
        current_game.other_player = current_game.p2
    else:
        current_game.other_player = current_game.p1
    match int(command[0]):
        case 0:  # AUX - Auxiliary
            match cmd_arg:
                case 0 | 1 | 4 | 7:
                    should_switch = False
                case 2:  # Suspend
                    save_title = "fs_save_" + input("Enter save name: ")
                    save_file = open(save_title, "w")
                    save_file.write(current_game.game_log)
                    return False
                case 3:  # Resume suspended game
                    save_name = "fs_save_" + input("Enter the name of the save file: fs_save_")
                    if not os.path.isfile(save_name):
                        input("Could not find save file " + save_name +
                              "\nPress Enter to continue...")
                        should_switch = False
                    else:
                        current_game = Game(True, open(save_name))
                        input("Loaded save file\nPress Enter to continue...")
                        current_game.p1.name = read_line_input("Enter name of Player 1: ")
                        current_game.p2.name = read_line_input("Enter name of Player 2: ")
                    return True
                case 6:  # Dispute
                    if current_game.other_player.cheated:
                        print("\nPlayer " + str(current_game.other_player.player_id)
                              + ": Game over - Called out for rule breakage\n[PLAYER " + str(
                            current_game.current_player.player_id) + " VICTORY]\n")
                        input("Press Enter to continue...")
                        return False
                case 8:  # Request Draw
                    clear_terminal()
                    print("Player " + str(current_game.current_player.player_id) + ": Request draw")
                    if input("Player " + str(current_game.other_player.player_id) + " response: ") == "01":
                        clear_terminal()
                        print_player_info(current_game.p1)
                        print_player_info(current_game.p2)
                        print_board()
                        print("Game concluded: Draw by mutual agreement")
                        input("Press Enter to continue...")
                        return False
                    should_switch = False
                case 9:  # Concede
                    print("\nPlayer " + str(current_game.current_player.player_id)
                          + ": Concede\n[PLAYER " + str(
                        current_game.other_player.player_id) + " VICTORY]\n")
                    input("Press Enter to continue...")
                    return False

        case 1:  # SWC - Switch
            current_game.current_player.selected_op = current_game.current_player.ops[cmd_arg]
            should_switch = False

        case 2:  # MOV - Move
            to_move = current_game.current_player.selected_op
            check_overwatch()
            if to_move == current_game.current_player.selected_op:
                current_game.board.contents[current_game.current_player.selected_op.location].remove(
                    current_game.current_player.selected_op)
                current_game.board.contents[cmd_arg].append(current_game.current_player.selected_op)
                current_game.current_player.selected_op.location = cmd_arg
                check_overwatch()

        case 3:  # HIT - Attack
            if current_game.other_player.ops[cmd_arg].reserve:
                current_game.current_player.cheated = True
            if current_game.current_player.selected_op.skill_active == 1 and \
                    (int(current_game.current_player.selected_op.op_id[1]) == (1 or 6)):
                # Move blade to target's sector
                current_game.board.contents[current_game.current_player.selected_op.location].remove(
                    current_game.current_player.selected_op)
                current_game.board.contents[current_game.other_player.ops[cmd_arg].location].append(
                    current_game.current_player.selected_op)
                current_game.current_player.selected_op.location = current_game.other_player.ops[cmd_arg].location
                # Deal damage to target
                current_game.other_player.ops[cmd_arg].take_damage(check_range(
                    current_game.current_player.selected_op, current_game.other_player.ops[cmd_arg], False, True))
            else:
                current_game.other_player.ops[cmd_arg].take_damage(check_range(
                    current_game.current_player.selected_op, current_game.other_player.ops[cmd_arg], False, False))

        case 4:  # RNF - Reinforce
            current_game.current_player.crates -= 1
            selected_facility = current_game.current_player.get_facility_by_index(cmd_arg)
            selected_facility.allocated += 1

        case 5:  # WDR - Withdraw
            current_game.current_player.crates += 1
            selected_facility = current_game.current_player.get_facility_by_index(cmd_arg)
            selected_facility.allocated -= 1
            should_switch = False

        case 6:  # RGP - Regroup
            rgp_target = current_game.current_player.ops[cmd_arg]
            switch_reserve_status(rgp_target, False)

        case 7:  # OVW - Overwatch
            current_game.overwatch_state = True
            current_game.overwatch_operator = current_game.current_player.ops[cmd_arg]

        case 8:  # SKL - Skill
            if current_game.current_player.skill_delay > 0:
                current_game.current_player.cheated = True
            match cmd_arg:
                case 0 | 5:  # Longwatch
                    current_game.current_player.ops[cmd_arg].skill_active = 1
                    current_game.current_player.skill_delay = 6
                case 1 | 6:  # Blade
                    current_game.current_player.ops[cmd_arg].skill_active = 1
                    current_game.current_player.skill_delay = 6
                    should_switch = False

        case 9:  # SPT - Support
            if current_game.current_player.artillery.facility_aux == 1:
                current_game.current_player.support_delay = 5 - current_game.current_player.command_center.allocated
                current_game.current_player.artillery.facility_aux = 0
                for op in current_game.board.contents[cmd_arg]:
                    if op.team == current_game.other_player.player_id:
                        op.take_damage(current_game.current_player.artillery.allocated + 1)
            else:
                selected_facility = current_game.current_player.get_facility_by_index(cmd_arg)
                match cmd_arg:
                    case 0:
                        selected_facility.facility_aux = 1
                    case 1:
                        for op in current_game.current_player.ops:
                            if op.hp < 5 and not op.reserve:
                                op.hp += 2
                                if op.hp > 5:
                                    op.hp = 5
                    case 2:
                        for op in current_game.current_player.ops:
                            switch_reserve_status(op, True)
                    case _:
                        should_switch = False

        case _:
            should_switch = False
    # Reset overwatch by changing overwatch operator to a reserve or dead operator
    if current_game.overwatch_state and current_game.overwatch_operator.team == current_game.other_player.player_id:
        current_game.overwatch_state = False
        for operator in current_game.other_player.ops:
            if operator.reserve or not operator.alive:
                current_game.overwatch_operator = operator
                break

    check_cooldowns()
    if should_switch:
        if current_game.current_player == current_game.p1:
            current_game.current_player = current_game.p2
        else:
            current_game.current_player = current_game.p1
    return True


# MAIN #
clear_terminal()
current_game.p1.name = read_line_input("Enter name of Player 1: ")
current_game.p2.name = read_line_input("Enter name of Player 2: ")
clear_terminal()
current_game.game_log += current_game.p1.name + "\n" + current_game.p2.name + "\n"
print_player_info(current_game.p1)
print_player_info(current_game.p2)
print_board()
while not current_game.is_finished:
    cmd = read_command_input("Player " + str(current_game.current_player.player_id) +
                             " (" + current_game.current_player.selected_op.op_id + "): ")

    if not validate_command(cmd):
        print("'" + cmd + "' is not a valid command.")
        continue
    if not parse_command(cmd):
        break

    # Print updated info
    clear_terminal()
    if not print_player_info(current_game.p1):
        break
    if not print_player_info(current_game.p2):
        break
    print_board()
