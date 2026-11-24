"""Generic fallback layout — renders all fields as a simple grouped table."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dndpy.card import formatters as fmt
from dndpy.db import repository as repo

console = Console()


def render(char, ruleset, db):
    stats = char.as_dict()
    derived = ruleset.compute_derived(stats)
    stats.update(derived)

    items = repo.list_items(db, char)

    console.print(Panel(
        f'[bold white]{char.name}[/]  [dim]({ruleset.FULL_NAME})[/]',
        style='blue', padding=(0, 2)
    ))
    console.print()

    sections = ruleset.field_sections()
    for section_name, fields in sections.items():
        table = Table.grid(padding=(0, 2))
        table.add_column(style='dim', min_width=20)
        table.add_column()
        for fd in fields:
            val = stats.get(fd.key)
            table.add_row(fd.label, fmt.stat_or_dash(val))
        console.print(Panel(table, title=f'[bold]{section_name.upper()}[/]',
                            border_style='blue', padding=(0, 1)))
        console.print()

    if items:
        table = Table.grid(padding=(0, 1))
        table.add_column(style='dim')
        table.add_column()
        table.add_column(justify='right', style='dim')
        for item in items:
            table.add_row('•', item.name, f'×{item.quantity}')
        console.print(Panel(table, title=f'[bold]EQUIPMENT[/] ({len(items)})',
                            border_style='cyan', padding=(0, 1)))
