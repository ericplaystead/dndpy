"""Item management: add, list, remove."""
from rich.console import Console
from rich.table import Table
from dndpy.cli.menus import BACK
from dndpy.cli import prompts
from dndpy.db import repository as repo

console = Console()


def items_menu(session: dict):
    from dndpy.cli.menus import Menu, MenuItem
    char = session.get('character')
    if not char:
        prompts.warn('No character loaded.')
        return

    menu = Menu(f'Items — {char.name}', [
        MenuItem('1', 'Add item',    add_item),
        MenuItem('2', 'List items',  list_items),
        MenuItem('3', 'Remove item', remove_item),
        MenuItem('0', 'Back',        lambda s: BACK),
    ], session)
    menu.run()


def add_item(session: dict):
    char = session.get('character')
    db = session['db']

    name = prompts.ask('Item name')
    if not name:
        return
    qty_str = prompts.ask('Quantity', default='1')
    try:
        qty = int(qty_str)
    except ValueError:
        qty = 1
    weight = prompts.ask('Weight (optional)', default='')
    notes = prompts.ask('Notes (optional)', default='')

    item = repo.add_item(db, char, name=name, quantity=qty,
                         weight=weight, notes=notes)
    prompts.info(f'✓ Added: {item.name} ×{item.quantity}')


def list_items(session: dict):
    char = session.get('character')
    db = session['db']

    items = repo.list_items(db, char)
    if not items:
        prompts.warn(f'{char.name} is carrying nothing.')
        return

    table = Table(title=f'{char.name}\'s Inventory', header_style='bold blue')
    table.add_column('#', style='dim')
    table.add_column('Item')
    table.add_column('Qty', justify='right')
    table.add_column('Weight')
    table.add_column('Notes')
    for i, item in enumerate(items, 1):
        table.add_row(str(i), item.name, str(item.quantity),
                      item.weight or '', item.notes or '')
    console.print(table)


def remove_item(session: dict):
    char = session.get('character')
    db = session['db']

    items = repo.list_items(db, char)
    if not items:
        prompts.warn('No items to remove.')
        return

    chosen = prompts.ask_choice(
        'Select item to remove',
        choices=items,
        display=[f'{i.name} ×{i.quantity}' for i in items],
    )
    if prompts.confirm(f'Remove "{chosen.name}"?'):
        repo.remove_item(db, chosen)
        prompts.info(f'✓ Removed: {chosen.name}')
