"""
Card renderer dispatcher.
Selects the right layout based on the ruleset's CARD_LAYOUT attribute.
"""
from rich.console import Console

console = Console()

_LAYOUTS = {
    'dnd':     'dndpy.card.layouts.dnd_layout',
    'coc':     'dndpy.card.layouts.coc_layout',
    'generic': 'dndpy.card.layouts.generic_layout',
}


def print_card(char, ruleset, db):
    """Print the character card to the terminal."""
    layout_id = getattr(ruleset, 'CARD_LAYOUT', 'generic')
    module_path = _LAYOUTS.get(layout_id, _LAYOUTS['generic'])

    import importlib
    layout = importlib.import_module(module_path)
    layout.render(char, ruleset, db)
