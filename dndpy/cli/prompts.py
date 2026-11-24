"""
Styled input helpers using rich.
All user prompts go through here — keeps formatting consistent
and makes it easy to swap out later (e.g. for a web form layer).
"""
from typing import Any, Callable, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()


def ask(label: str, default: Any = None, validator: Optional[Callable] = None,
        password: bool = False) -> str:
    """
    Prompt for a text value. Re-prompts on validation failure.
    validator: callable(str) -> (value, error_msg|None)
    """
    default_str = str(default) if default is not None else None
    while True:
        value = Prompt.ask(
            f'[bold cyan]{label}[/]',
            default=default_str,
            password=password,
            console=console,
        )
        # Rich may return None for empty input; normalize to empty string
        if value is None:
            value = ''
        if validator:
            coerced, err = validator(value)
            if err:
                console.print(f'  [red]✗ {err}[/]')
                continue
            return coerced
        return value


def ask_int(label: str, default: Optional[int] = None,
            min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """Prompt for an integer with optional bounds."""
    from dndpy.utils.validators import validate_int
    hint = ''
    if min_val is not None and max_val is not None:
        hint = f' ({min_val}–{max_val})'
    elif min_val is not None:
        hint = f' (≥{min_val})'

    default_str = str(default) if default is not None else None
    while True:
        raw = Prompt.ask(
            f'[bold cyan]{label}{hint}[/]',
            default=default_str,
            console=console,
        )
        if raw is None:
            raw = ''
        if not raw.strip() and default is not None:
            return default
        v, err = validate_int(raw)
        if err:
            console.print(f'  [red]✗ {err}[/]')
            continue
        if min_val is not None and v < min_val:
            console.print(f'  [red]✗ Must be at least {min_val}[/]')
            continue
        if max_val is not None and v > max_val:
            console.print(f'  [red]✗ Must be at most {max_val}[/]')
            continue
        return v


def ask_choice(label: str, choices: list, display: Optional[list] = None) -> Any:
    """
    Show a numbered list and return the chosen item.
    choices: list of values to return
    display: list of strings to show (defaults to str(choice))
    """
    display = display or [str(c) for c in choices]
    console.print(f'\n[bold]{label}[/]')
    for i, d in enumerate(display, 1):
        console.print(f'  [dim]{i}.[/] {d}')
    while True:
        raw = Prompt.ask('[bold cyan]Select[/]', console=console)
        if raw is None:
            raw = ''
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except (ValueError, TypeError):
            pass
        console.print(f'  [red]✗ Enter a number between 1 and {len(choices)}[/]')


def confirm(label: str, default: bool = False) -> bool:
    return Confirm.ask(f'[bold cyan]{label}[/]', default=default, console=console)


def info(msg: str):
    console.print(f'[green]{msg}[/]')


def warn(msg: str):
    console.print(f'[yellow]{msg}[/]')


def error(msg: str):
    console.print(f'[red]{msg}[/]')
