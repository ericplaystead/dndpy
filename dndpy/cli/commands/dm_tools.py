"""DM Tools: dice rolling and utilities."""
from rich.console import Console
from rich.panel import Panel
from dndpy.cli.menus import BACK
from dndpy.cli import prompts
from dndpy.utils.dice import DICE_OPTIONS, roll, roll_notation, roll_xdy

console = Console()


def dm_tools_menu(session: dict):
    from dndpy.cli.menus import Menu, MenuItem
    items = []
    for sides in DICE_OPTIONS:
        s = sides  # capture
        items.append(MenuItem(str(sides), f'Roll d{sides}', lambda sess, d=s: roll_single(sess, d)))
    items += [
        MenuItem('m', 'Roll multiple dice (NdX)', roll_multi),
        MenuItem('n', 'Roll dice notation (e.g. 2d6+3)', roll_from_notation),
        MenuItem('0', 'Back', lambda s: BACK),
    ]
    menu = Menu('DM Tools — Dice Roller', items, session)
    menu.run()


def roll_single(session: dict, sides: int):
    result = roll(sides)
    _show_roll(f'd{sides}', result, sides)


def roll_multi(session: dict):
    count = prompts.ask_int('How many dice', default=1, min_val=1)
    sides = prompts.ask_choice('Die size', choices=DICE_OPTIONS,
                               display=[f'd{d}' for d in DICE_OPTIONS])
    rolls = roll_xdy(count, sides)
    total = sum(rolls)
    breakdown = ' + '.join(str(r) for r in rolls)
    console.print(Panel(
        f'[bold]{count}d{sides}[/]\n'
        f'Rolls: [cyan]{breakdown}[/]\n'
        f'Total: [bold yellow]{total}[/]',
        title='Dice Roll', style='green'
    ))


def roll_from_notation(session: dict):
    from dndpy.utils.validators import validate_dice_str
    notation = prompts.ask('Notation (e.g. 2d6+3)', validator=validate_dice_str)
    result = roll_notation(notation)
    _show_roll(notation, result, None)


def _show_roll(label: str, result: int, sides):
    color = 'bold yellow'
    if sides and result == sides:
        color = 'bold green'
    elif sides and result == 1:
        color = 'bold red'
    console.print(Panel(
        f'[bold]{label}[/]  →  [{color}]{result}[/]',
        title='Dice Roll', style='green', expand=False
    ))
