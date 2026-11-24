"""
Pure formatting functions for card display.
No rich imports here — return plain strings or rich markup strings.
"""


def ability_cell(score, mod=None) -> str:
    """Format an ability score with optional modifier: '18 [dim](+4)[/]'"""
    if score is None:
        return '[dim]--[/]'
    s = str(score)
    if mod is not None:
        sign = '+' if mod >= 0 else ''
        return f'{s} [dim]({sign}{mod})[/]'
    return s


def hp_display(current, maximum) -> str:
    """Color-coded HP: green > 50%, yellow > 25%, red otherwise."""
    if current is None:
        return '[dim]--[/]'
    if maximum:
        try:
            ratio = int(current) / int(maximum)
        except (ValueError, ZeroDivisionError):
            ratio = 1.0
        color = 'green' if ratio > 0.5 else ('yellow' if ratio > 0.25 else 'red')
    else:
        color = 'white'
    maxstr = f' / {maximum}' if maximum is not None else ''
    return f'[{color}]{current}[/]{maxstr}'


def save_cell(value) -> str:
    if value is None:
        return '[dim]--[/]'
    sign = '+' if int(value) >= 0 else ''
    return f'{sign}{value}'


def stat_or_dash(value) -> str:
    if value is None or value == '':
        return '[dim]--[/]'
    return str(value)


def sanity_display(current, maximum) -> str:
    """Like hp_display but for sanity — red when low is more dramatic."""
    if current is None:
        return '[dim]--[/]'
    if maximum:
        try:
            ratio = int(current) / int(maximum)
        except (ValueError, ZeroDivisionError):
            ratio = 1.0
        color = 'cyan' if ratio > 0.66 else ('yellow' if ratio > 0.33 else 'bold red')
    else:
        color = 'cyan'
    maxstr = f' / {maximum}' if maximum is not None else ''
    return f'[{color}]{current}[/]{maxstr}'
