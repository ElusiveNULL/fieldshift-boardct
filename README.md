# FieldShift BoardCT
A tool to allow for playing my original game, FieldShift. FieldShift is a simple 1v1 turn-based strategy game played in the CLI.

The tool first takes each player's commands as input and calculates the result based on the game's rules. Afterwards, it prints the updated information on each player's resources as well as the updated contents of the board. This process repeats until a player wins.

The game's manual is included as a PDF. *It is intentionally designed to look complex in theory but to be simple in practice.*

\[Version advisory\] The current version is fully playable with the LSTD ruleset. However, the STDEX and STDEX Type-A rulesets have not yet been implemented.

## How to use
To start a game, both players must start the tool and enter their names when prompted. Players must communicate their commands to each other externally, then enter them into the tool. For example, if player one chose `25`, both player one and player two would enter `25` into BoardCT and the tool would then end player one's turn.

![Screenshot of the tool in use](boardct-screenshot.png)

## Installation
Binaries for Windows 10/11 and Linux are available in the releases section. The original Python file in the repository also includes a `#!` for quicker execution on Linux systems when moved to a directory on the `$PATH`.

## Credits
[JJ-Shep](https://github.com/JJ-Shep): Game rules and manual, balancing, programming and testing

[fp-58](https://github.com/fp-58): Programming and testing, efficiency and organization improvements
