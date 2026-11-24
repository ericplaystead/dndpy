"""
D&D / Pathfinder character card layout.
Used by dnd35, dnd35sub, and pathfinder rulesets.
"""
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dndpy.card import formatters as fmt
from dndpy.db import repository as repo

console = Console()

ABILITY_ORDER = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
ABILITY_SHORTS = {'strength': 'STR', 'dexterity': 'DEX', 'constitution': 'CON',
                  'intelligence': 'INT', 'wisdom': 'WIS', 'charisma': 'CHA'}
MOD_KEYS = {'strength': 'str_mod', 'dexterity': 'dex_mod', 'constitution': 'con_mod',
            'intelligence': 'int_mod', 'wisdom': 'wis_mod', 'charisma': 'cha_mod'}


def render(char, ruleset, db):
    stats = char.as_dict()
    derived = ruleset.compute_derived(stats)
    stats.update(derived)

    items = repo.list_items(db, char)
    creatures = repo.list_owned_creatures(db, char.id)

    _render_header(char, stats)
    console.print()

    left = _build_ability_panel(stats)
    right = _build_combat_panel(stats)
    console.print(Columns([left, right], equal=False, expand=True))
    console.print()

    saves_panel = _build_saves_panel(stats)
    inventory_panel = _build_inventory_panel(items)
    console.print(Columns([saves_panel, inventory_panel], equal=False, expand=True))

    if creatures:
        console.print()
        _render_companions(creatures)


def _render_header(char, stats):
    name = char.name
    class_ = stats.get('class_', '')
    level = stats.get('level', '')
    race = stats.get('race', '')
    alignment = stats.get('alignment', '')
    size = stats.get('size', '')
    campaign = stats.get('campaign', '')
    gender = stats.get('gender', '')

    identity_parts = [p for p in [class_, f'Level {level}' if level else '', race, alignment] if p]
    meta_parts = [p for p in [size, gender, f'Campaign: {campaign}' if campaign else ''] if p]

    header = Text()
    header.append(name, style='bold white')
    if identity_parts:
        header.append(f'\n{" | ".join(identity_parts)}', style='cyan')
    if meta_parts:
        header.append(f'\n{" | ".join(meta_parts)}', style='dim')

    console.print(Panel(header, style='blue', padding=(0, 2)))


def _build_ability_panel(stats) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style='bold', min_width=4)
    table.add_column(justify='right', min_width=3)
    table.add_column(style='dim', min_width=6)

    for key in ABILITY_ORDER:
        score = stats.get(key)
        mod = stats.get(MOD_KEYS.get(key, ''))
        table.add_row(ABILITY_SHORTS[key], fmt.ability_cell(score), f'({("+" if (mod or 0) >= 0 else "")}{mod})' if mod is not None else '')

    return Panel(table, title='[bold]ABILITY SCORES[/]', border_style='green', padding=(0, 1))


def _build_combat_panel(stats) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style='dim', min_width=12)
    table.add_column()

    hp = fmt.hp_display(stats.get('hit_points'), stats.get('hit_points_max'))
    table.add_row('Hit Points', hp)
    table.add_row('Armor Class', fmt.stat_or_dash(stats.get('armor_class')))
    table.add_row('Touch AC', fmt.stat_or_dash(stats.get('touch_ac')))
    table.add_row('Flat-Foot AC', fmt.stat_or_dash(stats.get('flatfoot_ac')))
    table.add_row('Initiative', fmt.save_cell(stats.get('initiative')))
    table.add_row('Speed', f"{stats.get('speed', '--')} ft" if stats.get('speed') else '[dim]--[/]')
    table.add_row('BAB', fmt.save_cell(stats.get('base_attack')))
    table.add_row('CMB', fmt.save_cell(stats.get('cmb')))
    table.add_row('CMD', fmt.stat_or_dash(stats.get('cmd')))

    xp = stats.get('experience')
    if xp is not None:
        table.add_row('XP', str(xp))

    return Panel(table, title='[bold]COMBAT[/]', border_style='red', padding=(0, 1))


def _build_saves_panel(stats) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style='dim')
    table.add_column(justify='right')

    table.add_row('Fortitude', fmt.save_cell(stats.get('save_fortitude')))
    table.add_row('Reflex',    fmt.save_cell(stats.get('save_reflex')))
    table.add_row('Will',      fmt.save_cell(stats.get('save_will')))

    return Panel(table, title='[bold]SAVING THROWS[/]', border_style='yellow', padding=(0, 1))


def _build_inventory_panel(items) -> Panel:
    if not items:
        content = Text('(empty)', style='dim')
    else:
        content = Table.grid(padding=(0, 1))
        content.add_column(style='dim', min_width=3)
        content.add_column()
        content.add_column(justify='right', style='dim')
        for item in items[:10]:  # cap at 10 on card, full list via items menu
            content.add_row('•', item.name, f'×{item.quantity}')
        if len(items) > 10:
            content.add_row('', f'[dim]...and {len(items)-10} more[/]', '')

    return Panel(content, title=f'[bold]EQUIPMENT[/] [dim]({len(items)})[/]',
                 border_style='cyan', padding=(0, 1))


def _render_companions(creatures):
    from rich.table import Table
    table = Table(title='COMPANIONS & CREATURES', header_style='bold magenta',
                  show_header=True, border_style='magenta')
    table.add_column('Type')
    table.add_column('Name')
    type_labels = {'familiar': 'Familiar', 'mount': 'Mount',
                   'companion': 'Companion', 'summoned': 'Summoned'}
    for c in creatures:
        table.add_row(type_labels.get(c.character_type, c.character_type), c.name)
    console.print(table)
