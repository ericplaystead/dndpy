import random
import re

DICE_RE = re.compile(r'^([1-9]\d*)d([1-9]\d*)([+-]\d+)?$')


def roll(sides: int) -> int:
    return random.randint(1, sides)


def d4() -> int:  return roll(4)
def d6() -> int:  return roll(6)
def d8() -> int:  return roll(8)
def d10() -> int: return roll(10)
def d12() -> int: return roll(12)
def d20() -> int: return roll(20)
def d100() -> int: return roll(100)


def roll_xdy(count: int, sides: int) -> list[int]:
    return [roll(sides) for _ in range(count)]


def roll_notation(notation: str) -> int:
    """
    Roll dice from a notation string like "2d6+3".
    Returns the total.
    """
    m = DICE_RE.match(notation.strip())
    if not m:
        raise ValueError(f'Invalid dice notation: {notation!r}')
    n, d, bonus = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    return sum(roll(d) for _ in range(n)) + bonus


DICE_OPTIONS = [4, 6, 8, 10, 12, 20]
