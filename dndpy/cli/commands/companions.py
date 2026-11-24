"""
Familiars, mounts, animal companions, summoned creatures.
All stored as Character rows with owner_id pointing to the PC.
"""
from rich.console import Console
from rich.table import Table
from dndpy.cli.menus import BACK
from dndpy.cli import prompts
from dndpy.db import repository as repo

console = Console()

_TYPE_LABELS = {
    'familiar':  'Familiar',
    'mount':     'Mount',
    'companion': 'Animal Companion',
    'summoned':  'Summoned Creature',
}


def companions_menu(session: dict):
    from dndpy.cli.menus import Menu, MenuItem
    char = session.get('character')
    if not char:
        prompts.warn('No character loaded.')
        return

    menu = Menu('Companions & Creatures', [
        MenuItem('1', 'Add familiar',            lambda s: add_creature(s, 'familiar')),
        MenuItem('2', 'Add animal companion',    lambda s: add_creature(s, 'companion')),
        MenuItem('3', 'Add mount',               lambda s: add_creature(s, 'mount')),
        MenuItem('4', 'Add summoned creature',   lambda s: add_creature(s, 'summoned')),
        MenuItem('5', 'List all companions',     list_companions),
        MenuItem('0', 'Back',                    lambda s: BACK),
    ], session)
    menu.run()


def add_creature(session: dict, creature_type: str):
    char = session.get('character')
    ruleset = session.get('ruleset')
    db = session['db']

    label = _TYPE_LABELS.get(creature_type, creature_type)
    prompts.info(f'\nAdding {label} for {char.name}')

    name = prompts.ask('Name')
    if not name:
        return

    creature = repo.create_character(
        db,
        name=name,
        ruleset_id=ruleset.RULESET_ID if ruleset else 'generic',
        campaign_id=char.campaign_id,
        character_type=creature_type,
        owner_id=char.id,
    )
    prompts.info(f'✓ {label} "{name}" added to {char.name}.')


def list_companions(session: dict):
    char = session.get('character')
    db = session['db']

    creatures = repo.list_owned_creatures(db, char.id)
    if not creatures:
        prompts.warn(f'{char.name} has no companions or creatures.')
        return

    table = Table(title=f'Companions of {char.name}', header_style='bold blue')
    table.add_column('Type')
    table.add_column('Name')
    for c in creatures:
        table.add_row(_TYPE_LABELS.get(c.character_type, c.character_type), c.name)
    console.print(table)
