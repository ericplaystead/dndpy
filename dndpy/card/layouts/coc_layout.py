"""
Call of Cthulhu character card layout.
Investigator sheet feel: characteristics, condition, investigator info.
"""
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dndpy.card import formatters as fmt
from dndpy.db import repository as repo

console = Console()

CHARACTERISTICS = [
    ('strength',     'STR'),
    ('dexterity',    'DEX'),
    ('intelligence', 'INT'),
    ('constitution', 'CON'),
    ('appearance',   'APP'),
    ('power',        'POW'),
    ('size',         'SIZ'),
    ('education',    'EDU'),
]


def render(char, ruleset, db):
    stats = char.as_dict()
    derived = ruleset.compute_derived(stats)

    items = repo.list_items(db, char)
    creatures = repo.list_owned_creatures(db, char.id)

    _render_header(char, stats)
    console.print()

    left = _build_characteristics_panel(stats)
    right = _build_condition_panel(stats, derived)
    console.print(Columns([left, right], equal=False, expand=True))
    console.print()

    info_panel = _build_investigator_panel(stats, derived)
    inventory_panel = _build_inventory_panel(items)
    console.print(Columns([info_panel, inventory_panel], equal=False, expand=True))

    if creatures:
        console.print()
        _render_companions(creatures)


def _render_header(char, stats):
    name = char.name
    full_name = stats.get('full_name', '')
    occupation = stats.get('occupation', '')
    age = stats.get('age', '')
    nationality = stats.get('nationality', '')
    campaign = stats.get('campaign', '')

    header = Text()
    header.append(name, style='bold white')
    if full_name and full_name != name:
        header.append(f' ({full_name})', style='dim')
    parts = [p for p in [occupation, f'Age {age}' if age else '', nationality] if p]
    if parts:
        header.append(f'\n{" | ".join(parts)}', style='cyan')
    if campaign:
        header.append(f'\nCampaign: {campaign}', style='dim')

    console.print(Panel(header, style='magenta', padding=(0, 2)))


def _build_characteristics_panel(stats) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style='bold', min_width=4)
    table.add_column(justify='right', min_width=3)
    table.add_column(style='dim', min_width=8)

    for key, short in CHARACTERISTICS:
        score = stats.get(key)
        half = int(score) // 2 if score is not None else None
        fifth = int(score) // 5 if score is not None else None
        sub = f'½{half} ⅕{fifth}' if half is not None else ''
        table.add_row(short, fmt.stat_or_dash(score), sub)

    return Panel(table, title='[bold]CHARACTERISTICS[/]', border_style='green', padding=(0, 1))


def _build_condition_panel(stats, derived) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style='dim', min_width=14)
    table.add_column()

    hp = fmt.hp_display(stats.get('hit_points'), stats.get('hit_points_max'))
    san = fmt.sanity_display(stats.get('sanity'), stats.get('sanity_max'))
    mp_display = fmt.hp_display(stats.get('magic_points'), stats.get('magic_points_max'))

    table.add_row('Hit Points',     hp)
    table.add_row('Sanity',         san)
    table.add_row('Magic Points',   mp_display)
    table.add_row('Luck',           fmt.stat_or_dash(stats.get('luck')))

    db_text = derived.get('damage_bonus')
    if db_text:
        table.add_row('Damage Bonus',   db_text)

    idea = derived.get('idea')
    know = derived.get('know')
    if idea is not None:
        table.add_row('Idea',           str(idea))
    if know is not None:
        table.add_row('Know',           str(know))

    return Panel(table, title='[bold]CONDITION[/]', border_style='red', padding=(0, 1))


def _build_investigator_panel(stats, derived) -> Panel:
    table = Table.grid(padding=(0, 1))
    table.add_column(style='dim', min_width=14)
    table.add_column()

    for label, key in [
        ('Occupation', 'occupation'),
        ('Nationality', 'nationality'),
        ('Residence',  'residence'),
        ('Birthplace', 'birthplace'),
        ('Sex', 'sex'),
        ('Age', 'age'),
    ]:
        val = stats.get(key)
        if val:
            table.add_row(label, str(val))

    return Panel(table, title='[bold]INVESTIGATOR[/]', border_style='yellow', padding=(0, 1))


def _build_inventory_panel(items) -> Panel:
    if not items:
        content = Text('(empty)', style='dim')
    else:
        content = Table.grid(padding=(0, 1))
        content.add_column(style='dim', min_width=2)
        content.add_column()
        content.add_column(justify='right', style='dim')
        for item in items[:10]:
            content.add_row('•', item.name, f'×{item.quantity}')
        if len(items) > 10:
            content.add_row('', f'[dim]...and {len(items)-10} more[/]', '')

    return Panel(content, title=f'[bold]EQUIPMENT[/] [dim]({len(items)})[/]',
                 border_style='cyan', padding=(0, 1))


def _render_companions(creatures):
    table = Table(title='COMPANIONS', header_style='bold magenta', show_header=True)
    table.add_column('Type')
    table.add_column('Name')
    for c in creatures:
        table.add_row(c.character_type, c.name)
    console.print(table)
