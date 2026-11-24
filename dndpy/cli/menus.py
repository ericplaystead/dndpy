"""
Interactive menu engine.
A Menu is a list of MenuItems rendered via rich. Each item has a key and a handler.
Handlers return BACK to go up a level, EXIT to quit, or None to stay.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

BACK = object()
EXIT = object()


@dataclass
class MenuItem:
    key: str
    label: str
    handler: Callable
    # If True, this item is only shown/active when condition(session) is True
    condition: Optional[Callable] = None


class Menu:
    def __init__(self, title: str, items: list[MenuItem], session: dict,
                 subtitle: str = ''):
        self.title = title
        self.items = items
        self.session = session
        self.subtitle = subtitle

    def _active_items(self) -> list[MenuItem]:
        return [
            item for item in self.items
            if item.condition is None or item.condition(self.session)
        ]

    def _render_header(self):
        char = self.session.get('character')
        ruleset = self.session.get('ruleset')

        status_parts = []
        if char:
            status_parts.append(f'[bold green]{char.name}[/]')
        else:
            status_parts.append('[dim]No character loaded[/]')
        if ruleset:
            status_parts.append(f'[dim]{ruleset.FULL_NAME}[/]')

        status = '  |  '.join(status_parts)
        console.print(Panel(
            f'[bold white]{self.title}[/]\n{status}',
            style='blue',
            expand=False,
            padding=(0, 2),
        ))

    def _render_items(self, active: list[MenuItem]):
        table = Table.grid(padding=(0, 2))
        table.add_column(style='bold yellow', min_width=4)
        table.add_column()
        for item in active:
            table.add_row(f'\\[{item.key}]', item.label)
        console.print(table)
        console.print()

    def run(self):
        """Run the menu loop. Returns EXIT sentinel if user wants to quit."""
        from dndpy.cli.prompts import console as pc
        while True:
            console.print()
            self._render_header()
            active = self._active_items()
            self._render_items(active)
            raw = console.input('[bold cyan]> [/]').strip()
            key = raw.lower()

            matched = next((item for item in active if item.key.lower() == key), None)
            if matched is None:
                console.print(f'[red]  Invalid option: {raw!r}[/]')
                continue

            result = matched.handler(self.session)
            if result is EXIT:
                return EXIT
            if result is BACK:
                return BACK
            # None or anything else: stay in this menu
