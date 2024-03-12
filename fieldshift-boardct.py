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
        self.game_log = ""  # Contains log of every command for saving and loading

        self.is_in_playback = is_in_playback  # Tracks whether game is reading from save file
        self.input_stream = input_stream

        p1 = create_player("No name", 1)
        p2 = create_player("No name", 2)
        board = Battlefield([], [])
        create_sectors(board)
        # First 5 operators are not in reserve
        board.contents[0].extend(p1.ops[:5])
        board.contents[9].extend(p2.ops[:5])

        ruleset = 0
        self.operator_atk = 3
        self.ruleset = ruleset
        self.p1 = p1
        self.p2 = p2
        self.board = board
        self.ops_bleeding_out = list()
        self.current_player = p1
        self.other_player = p2

        self.overwatch_state = False
        self.overwatch_operator = p1.ops[5]


class Operator:
    max_hp = 5

    def __init__(self, hp: int, op_id: str, team: int, reserve: bool, location: int, alive: bool,
                 skill_active: int, bleeding_out: int):
        self.hp = hp
        self.op_id = op_id
        self.team = team
        self.reserve = reserve
        self.location = location
        self.alive = alive
        self.skill_active = skill_active
        self.bleeding_out = bleeding_out

    def take_damage(self, dmg_amount: int):
        self.hp -= dmg_amount
        if self.hp < 1:  # Kill operator
            self.alive = False
            self.skill_active = 0
            self.bleeding_out = 5
            if dmg_amount == 8:  # Only the sniper's skill can deal this much damage
                self.bleeding_out = 6  # The sniper's skill occurs on the target's turn, so the timer must be extended
            current_game.ops_bleeding_out.append(self)
            for op in current_game.current_player.ops:  # Change selected operator to first alive and deployed operator
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
    player_char = '+'  # This variable indicates which player controls the operator
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
        result.append(Operator(5, id_list[i], player_num, is_reserve, starting_sector, True, 0, 5))
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
        if not is_support:  # Take crate unless triggered by support skill
            current_game.current_player.crates -= 1
        operator.reserve = False
        if current_game.current_player == current_game.p1:
            current_game.board.contents[0].append(operator)
            operator.location = 0
        else:
            current_game.board.contents[9].append(operator)
            operator.location = 9
    else:
        if not is_support:
            current_game.current_player.crates += 1
        operator.reserve = True
        # Remove operator from the board and select new operator
        current_game.board.contents[operator.location].remove(operator)
        if current_game.ruleset == 0 and current_game.current_player.selected_op == operator:
            for op in current_game.current_player.ops:
                if op.alive and not op.reserve:
                    current_game.current_player.selected_op = op
                    break


# Check if attack is in range, factor in class/terrain, and return net damage
def check_range(attacker: Operator, target: Operator, automatic: bool, assassinate: bool):
    net_range = 3
    if current_game.ruleset == -1:
        net_range = 2
    net_damage = current_game.operator_atk
    if attacker.op_id[1] == ("0" or "5"):  # If operator class is Longwatch
        net_range = 5
    match target.location:
        case 0 | 9:  # Ruins
            net_range -= 2
            net_damage -= 1
        case 1 | 8:  # Tall grass
            net_range -= 1
        case 4 | 5:  # Mountains
            net_damage += 1
    match attacker.location:
        case 0 | 9:
            net_range -= 2
        case 4 | 5:
            net_damage += 1
    if assassinate:  # If attack is blade's skill
        net_damage += 2
        net_range = 9
    elif attacker.op_id[1] == ("1" or "6"):  # Set blade's range to zero regardless of terrain
        net_range = 0
    if net_range < abs(attacker.location - target.location):
        if automatic:
            return 0
        return -1  # This is checked to warn the player of an out-of-range attack
    return net_damage


def check_cooldowns():
    if current_game.current_player.skill_delay > 0:
        current_game.current_player.skill_delay -= 1
    if current_game.current_player.support_delay > 0:
        # Decrease support cooldown more for each crate allocated to command center
        current_game.current_player.support_delay -= current_game.current_player.command_center.allocated + 1
        if current_game.current_player.support_delay < 0:
            current_game.current_player.support_delay = 0
    for op in current_game.ops_bleeding_out:
        if op.team == current_game.current_player.player_id:
            op.bleeding_out -= 1
            if op.bleeding_out == 0:
                current_game.board.contents[op.location].remove(op)
                current_game.ops_bleeding_out.remove(op)
    if current_game.current_player.medbay.facility_aux > 0:  # If medbay heal cooldown has not completed
        # Check if allocated crates +1 is less than passive healing cooldown
        if current_game.current_player.medbay.allocated + 1 <= current_game.current_player.medbay.facility_aux:
            # Decrease passive reserve healing cooldown by more for each crate allocated to medbay
            current_game.current_player.medbay.facility_aux -= current_game.current_player.medbay.allocated + 1
            # Keep cooldown from being negative
            if current_game.current_player.medbay.facility_aux < 0:
                current_game.current_player.medbay.facility_aux = 0
        else:
            current_game.current_player.medbay.facility_aux = 0
    else:
        heal_amount = 2
        # If enough crates are allocated to make cooldown zero, excess crates increase healing amount
        if current_game.current_player.medbay.allocated > 3:
            heal_amount += current_game.current_player.medbay.allocated - 3
        for op in current_game.current_player.ops:
            if op.reserve and op.hp < 5:
                op.hp += heal_amount
                if op.hp > 5:
                    op.hp = 5


# Check if an operator triggers an overwatch shot
def check_overwatch(to_check: Operator):
    longwatch = current_game.current_player.ops[0]
    # If the other player's longwatch skill is active
    if current_game.other_player.ops[0].skill_active == -1:
        longwatch = current_game.other_player.ops[0]
    # Check second longwatch as well
    elif current_game.other_player.ops[5].skill_active == -1:
        longwatch = current_game.other_player.ops[5]
    # Trigger longwatch skill shot if target operator is on other team
    if longwatch.team == current_game.other_player.player_id:
        to_check.take_damage(8)
        longwatch.skill_active = 0  # Disable longwatch skill
    # If overwatch is active and the overwatch operator is on the other team
    if current_game.overwatch_state and current_game.overwatch_operator.team == current_game.other_player.player_id:
        attack_check = check_range(
            current_game.overwatch_operator, to_check, True, False)
        # If the overwatch operator is alive and deployed and target is in range
        if (not current_game.overwatch_operator.reserve and current_game.overwatch_operator.alive) and \
                attack_check > 0:
            to_check.take_damage(attack_check)
            current_game.overwatch_state = False
            # Reset overwatch operator to dead or reserve operator because they aren't eligible to take overwatch shots
            for operator in current_game.other_player.ops:
                if operator.reserve or not operator.alive:
                    current_game.overwatch_operator = operator


def change_ruleset(current_ruleset: int):
    current_ruleset_name = "LSTD"
    target_ruleset_name = "STDEX"
    ruleset_destination = 1  # Ruleset to switch to
    if current_ruleset == 1:
        current_ruleset_name = target_ruleset_name
        target_ruleset_name += " Type-A"
        ruleset_destination = -1
        current_game.operator_atk = 2
    elif current_ruleset == -1:
        target_ruleset_name = current_ruleset_name
        current_ruleset_name = "STDEX Type-A"
        ruleset_destination = 0
    clear_terminal()
    print("Player " + str(current_game.current_player.player_id)
          + ": Request ruleset change (" + current_ruleset_name + " --> " + target_ruleset_name + ")")
    temp_input = input("Player " + str(current_game.other_player.player_id) + " response: ")
    if len(temp_input) > 0 and temp_input[-1] == "1":
        input("Ruleset changed to " + target_ruleset_name + "\n\nPress Enter to continue...")
        current_game.ruleset = ruleset_destination
        print_board()
    else:
        input("Cancelling ruleset change.\n\nPress Enter to continue...")
    clear_terminal()


def check_game_over(player: Player):
    for op in player.ops:
        if op.alive and not op.reserve:
            return False
    if player.player_id == current_game.current_player.player_id:
        print("Player " + str(current_game.current_player.player_id)
              + ": Game over - All deployed operators eliminated.\n[PLAYER " +
              str(current_game.other_player.player_id) + " VICTORY]\n")
    else:
        print("Player " + str(current_game.other_player.player_id)
              + ": Game over - All deployed operators eliminated.\n[PLAYER " +
              str(current_game.current_player.player_id) + " VICTORY]\n")
    input("Press Enter to continue...")
    return True


def move_operator(to_move: Operator, move_to: int):
    check_overwatch(to_move)  # Check if moving operator triggers overwatch shot
    # Currently selected operator will change if killed by overwatch shot
    if to_move.alive and (to_move == current_game.current_player.selected_op or current_game.ruleset != 0):
        current_game.board.contents[to_move.location].remove(to_move)
        current_game.board.contents[move_to].append(to_move)
        to_move.location = move_to
        check_overwatch(to_move)


def print_player_info(player: Player):
    print("[Player " + str(player.player_id) + ": " + player.name + "]" +
          "\nSkill Cooldown:", end=" ")
    if player.skill_delay > 0:  # If skill is ready, print [READY] instead of cooldown number
        print(str(player.skill_delay), end="")
    else:
        print("[READY]", end="")
    print("\nSupport Cooldown:", end=" ")
    if player.support_delay > 0:  # If support is ready, print [READY] instead of cooldown number
        print(str(player.support_delay))
    else:
        print("[READY]")
    print("Crates: " + str(player.crates) +
          "\nFacility Crates: " + str(player.artillery.allocated) +
          "-" + str(player.medbay.allocated) +
          "-" + str(player.command_center.allocated) +
          "\nReserve:", end=" ")
    # Print all operators that are alive and in reserve
    for op in player.ops:
        if op.alive:
            if op.reserve:
                if op.hp < 5:
                    print(str(player.ops.index(op)) + "v" + str(op.hp), end=" ")
                else:
                    print(str(player.ops.index(op)), end=" ")
    print("\n")


def print_board():
    print_player_info(current_game.p1)
    print_player_info(current_game.p2)
    # Print all sectors
    for i in range(10):
        print(current_game.board.terrain[i] + " Sector " + str(i) + ":", end=" ")
        for op in current_game.board.contents[i]:
            print(op.op_id, end="")
            if op.hp < 5:
                # Print remaining vitality if not full
                if op.alive:
                    print("v" + str(op.hp), end="")
                # If bleeding out, print cooldown instead
                elif not op.reserve:
                    print("X" + str(op.bleeding_out), end="")
            # If operator is on overwatch
            if current_game.overwatch_state and op == current_game.overwatch_operator:
                print("W", end="")
            # If operator's skill is active and permanent until used
            if op.skill_active == -1:
                print("S", end="")
            # If skill is active and lasts until a set number of turns
            elif op.skill_active > 0:
                print("S" + str(op.skill_active), end="")
            print("", end=" ")
        print("")
    print("\n")


def validate_command(command: str):
    return (len(command) == 2 or len(command) == 2 + abs(current_game.ruleset)) and command.isdecimal()


def parse_command(command):
    global current_game
    # Add command to game log unless save or load operation is done
    if not command == "02" and not command == "03" and not command == "05":
        current_game.game_log += command + "\n"
    # Reset the tracker for if the current player cheated
    current_game.current_player.cheated = False
    cmd_arg = int(command[1])
    extended_cmd = False
    cmd_arg_alt = 0
    if current_game.ruleset != 0:
        extended_cmd = True
        if len(cmd) == 3:
            cmd_arg = int(cmd[2])
            cmd_arg_alt = int(cmd[1])
    should_switch = True  # Tracks if the turn should end
    match int(command[0]):
        case 0:  # AUX - Auxiliary
            match cmd_arg:
                case 0 | 1 | 4 | 7:
                    should_switch = False
                case 2:  # Suspend
                    save_title = "fs_save_" + input("Enter save name: ")
                    save_file = open(save_title, "w")
                    temp_log = str(current_game.ruleset) + "\n" + current_game.game_log
                    current_game.game_log = temp_log
                    save_file.write(current_game.game_log)
                    return False
                case 3:  # Resume suspended game
                    save_name = "fs_save_" + input("Enter name of save file: fs_save_")
                    if not os.path.isfile(save_name):
                        input("Could not find save file: " + save_name +
                              "\n\nPress Enter to continue...")
                    else:  # Load save
                        current_game = Game(True, open(save_name))
                        input("Loaded save file\n\nPress Enter to continue...")
                        current_game.ruleset = int(read_line_input("Enter ruleset number: "))
                        current_game.p1.name = read_line_input("Enter name of Player 1: ")
                        current_game.p2.name = read_line_input("Enter name of Player 2: ")
                    should_switch = False
                case 5:  # Request change ruleset
                    should_switch = False
                    if current_game.ruleset == 0 or abs(current_game.ruleset) == 1:
                        change_ruleset(current_game.ruleset)
                case 6:  # Dispute
                    if current_game.other_player.cheated:
                        print("\nPlayer " + str(current_game.other_player.player_id)
                              + ": Game over - Called out for rule breakage\n[PLAYER " + str(
                            current_game.current_player.player_id) + " VICTORY]\n")
                        input("Press Enter to continue...")
                        return False
                case 8:  # Request draw
                    clear_terminal()
                    print("Player " + str(current_game.current_player.player_id) + ": Request draw")
                    if input("Player " + str(current_game.other_player.player_id) + " response: ") == "01":
                        clear_terminal()
                        print_board()
                        input("Game concluded: Draw by mutual agreement\n\nPress Enter to continue...")
                        return False
                    should_switch = False
                case 9:  # Concede
                    print("\nPlayer " + str(current_game.current_player.player_id)
                          + ": Concede\n[PLAYER " + str(
                        current_game.other_player.player_id) + " VICTORY]\n")
                    input("Press Enter to continue...")
                    return False

        case 1:  # SWC - Switch / SWP - Swap
            if extended_cmd:  # SWP
                temp_position = current_game.current_player.ops[cmd_arg].location
                move_operator(current_game.current_player.ops[cmd_arg],
                              current_game.current_player.ops[cmd_arg_alt].location)
                move_operator(current_game.current_player.ops[cmd_arg_alt], temp_position)
                check_overwatch(current_game.current_player.ops[cmd_arg])
            else:  # SWC
                if current_game.current_player.ops[cmd_arg].alive:
                    current_game.current_player.selected_op = current_game.current_player.ops[cmd_arg]
                should_switch = False

        case 2:  # MOV - Move
            if not extended_cmd:
                move_operator(current_game.current_player.selected_op, cmd_arg)
            else:
                if len(cmd) != 2:
                    if current_game.current_player.ops[cmd_arg_alt].reserve:
                        should_switch = False
                    else:
                        move_operator(current_game.current_player.ops[cmd_arg_alt], cmd_arg)
                else:
                    clear_terminal()
                    input("Command " + cmd + " is missing a third argument.\n\nPress Enter to continue...")
                    should_switch = False

        case 3:  # HIT - Attack
            target = current_game.other_player.ops[cmd_arg]
            attacker = current_game.current_player.selected_op
            if extended_cmd:
                attacker = current_game.current_player.ops[cmd_arg_alt]
            if target.reserve:
                current_game.current_player.cheated = True
            # Check for skills
            if attacker.skill_active != 0:
                match int(attacker.op_id[1]):
                    case 1 | 6:  # Blade
                        # Move blade to target's sector
                        current_game.board.contents[attacker.location].remove(attacker)
                        current_game.board.contents[target.location].append(attacker)
                        attacker.location = target.location
                        # Deal damage to target
                        damage = check_range(attacker, target, False, True)
                        if damage == -1:
                            clear_terminal()
                            input("Target out of range.\n\nPress enter to continue...")
                            clear_terminal()
                            should_switch = False
                        else:
                            target.take_damage(damage)
                    case 3 | 8:  # Medic
                        if current_game.current_player.ops[cmd_arg].alive:
                            should_switch = False
                        else:
                            target = current_game.current_player.ops[cmd_arg]
                            attacker.skill_active = 0
                            target.alive = True
                            target.hp = 5
                            target.bleeding_out = 6
                            if target.reserve:
                                current_game.current_player.cheated = True
                                target.reserve = False
                    case 4 | 9:  # Specialist
                        attacker.skill_active -= 1
                        damage = check_range(attacker, target, False, False)
                        if damage == -1:
                            clear_terminal()
                            input("Target out of range.\n\nPress enter to continue...")
                            clear_terminal()
                            should_switch = False
                        else:
                            target.take_damage(damage)
                        should_switch = False
            else:  # If skill not active
                damage = check_range(attacker, target, False, False)
                if damage == -1:
                    clear_terminal()
                    input("Target out of range.\n\nPress enter to continue...")
                    clear_terminal()
                    should_switch = False
                else:
                    target.take_damage(damage)

        case 4:  # RNF - Reinforce
            selected_facility = current_game.current_player.get_facility_by_index(cmd_arg)
            if cmd_arg > current_game.current_player.crates:
                current_game.current_player.cheated = True
            if current_game.ruleset != 0:
                current_game.current_player.crates -= 1
                selected_facility.allocated += 1
            else:
                if len(cmd) == 2:
                    clear_terminal()
                    input("Command " + cmd + " is missing a third argument.\n\nPress Enter to continue...")
                    should_switch = False
                else:
                    current_game.current_player.crates -= cmd_arg_alt
                    selected_facility.allocated += cmd_arg_alt

        case 5:  # WDR - Withdraw
            selected_facility = current_game.current_player.get_facility_by_index(cmd_arg)
            if cmd_arg > selected_facility.allocated:
                current_game.current_player.cheated = True
            if current_game.ruleset != 0:
                current_game.current_player.crates += 1
                selected_facility.allocated -= 1
                should_switch = False
            else:
                should_switch = False
                if len(cmd) == 2:
                    clear_terminal()
                    input("Command " + cmd + " is missing a third argument.\n\nPress Enter to continue...")
                else:
                    current_game.current_player.crates += cmd_arg_alt
                    selected_facility.allocated -= cmd_arg_alt

        case 6:  # RGP - Regroup
            if current_game.current_player.skill_delay > 0 or current_game.other_player.ops[2].skill_active > 0 \
                    or current_game.other_player.ops[7].skill_active > 0:
                current_game.current_player.cheated = True
            current_game.current_player.skill_delay = 6
            rgp_target = current_game.current_player.ops[cmd_arg]
            switch_reserve_status(rgp_target, False)

        case 7:  # OVW - Overwatch
            current_game.overwatch_state = True
            current_game.overwatch_operator = current_game.current_player.ops[cmd_arg]

        case 8:  # SKL - Skill
            # Mark cheating if skill was activated during cooldown or if SKL is banned by enemy technician
            if current_game.current_player.skill_delay > 0 or current_game.other_player.ops[2].skill_active > 0 \
                    or current_game.other_player.ops[7].skill_active > 0:
                current_game.current_player.cheated = True
            if not current_game.current_player.ops[cmd_arg].alive:
                should_switch = False
            else:
                current_game.current_player.skill_delay = 6
                match cmd_arg:
                    case 0 | 5:  # Longwatch
                        current_game.current_player.ops[cmd_arg].skill_active = -1
                    case 1 | 6 | 3 | 8:  # Blade or medic
                        current_game.current_player.ops[cmd_arg].skill_active = -1
                        should_switch = False
                    case 2 | 7:  # Technician
                        current_game.current_player.ops[cmd_arg].skill_active = 3
                    case 4 | 9:  # Specialist
                        current_game.current_player.ops[cmd_arg].skill_active = 3
                        should_switch = False

        case 9:  # SPT - Support
            # Mark cheating SPT is banned by enemy technician
            if current_game.other_player.ops[2].skill_active > 0 or current_game.other_player.ops[7].skill_active > 0:
                current_game.current_player.cheated = True
            current_game.current_player.support_delay = 6
            # Interpret argument as artillery target sector instead of facility number if artillery is loaded
            if current_game.current_player.artillery.facility_aux == 1:
                current_game.current_player.support_delay = 5 - current_game.current_player.command_center.allocated
                current_game.current_player.artillery.facility_aux = 0
                for op in current_game.board.contents[cmd_arg]:
                    if op.team == current_game.other_player.player_id:
                        op.take_damage(current_game.current_player.artillery.allocated + 1)
            else:  # Mark cheating if support was activated during cooldown
                if current_game.current_player.support_delay > 0:
                    current_game.current_player.cheated = True
                match cmd_arg:
                    case 0:  # Artillery
                        current_game.current_player.artillery.facility_aux = 1  # Load artillery
                    case 1:  # Medbay
                        for op in current_game.current_player.ops:
                            if op.hp < 5 and not op.reserve:
                                op.hp += 2
                                if op.hp > 5:
                                    op.hp = 5
                    case 2:  # Command center
                        for op in current_game.current_player.ops:
                            switch_reserve_status(op, True)
                        if extended_cmd:
                            for op in current_game.current_player.ops:
                                if current_game.ruleset == 0 and op.alive and not op.reserve:
                                    current_game.current_player.selected_op = op
                                    break
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

    if should_switch:
        check_cooldowns()
        if current_game.current_player == current_game.p1:
            current_game.current_player = current_game.p2
            current_game.other_player = current_game.p1
        else:
            current_game.current_player = current_game.p1
            current_game.other_player = current_game.p2
    return True


# MAIN #
clear_terminal()
current_game.p1.name = read_line_input("Enter name of Player 1: ")
current_game.p2.name = read_line_input("Enter name of Player 2: ")
clear_terminal()
# Remove colon and space before player name if player name is empty
if current_game.p1.name == "":
    current_game.p1.name = "\b\b"
if current_game.p2.name == "":
    current_game.p2.name = "\b\b"
current_game.game_log += current_game.p1.name + "\n" + current_game.p2.name + "\n"

while not current_game.is_finished:
    clear_terminal()
    print_board()
    # Check for win condition
    if check_game_over(current_game.current_player) or check_game_over(current_game.other_player):
        break
    print("Player " + str(current_game.current_player.player_id), end="")
    if current_game.ruleset == 0:
        print(" (" + current_game.current_player.selected_op.op_id + ")", end="")
    cmd = read_command_input(": ")

    if not validate_command(cmd):
        if cmd == "":
            input("No command entered.\n\nPress Enter to continue...")
        else:
            input("'" + cmd + "' is not a valid command.\n\nPress Enter to continue...")
        continue
    if not parse_command(cmd):
        break
