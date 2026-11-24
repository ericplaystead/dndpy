"""
RulesetBase — the interface contract every ruleset map must implement.

To create a custom ruleset, subclass RulesetBase and implement all
abstract methods. Drop the file in user_rulesets/ and it will be
discovered automatically on startup.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


SECTIONS = ('identity', 'ability', 'combat', 'saves', 'skills', 'condition', 'other')


@dataclass
class FieldDef:
    """
    Defines a single stat field for a ruleset.

    key             — stat_key in the database (e.g. "strength")
    label           — full display label (e.g. "Strength")
    short           — abbreviated label for card display (e.g. "STR")
    stat_type       — "int" or "text"
    section         — which card section this belongs to (see SECTIONS)
    required_on_create — whether to prompt during character creation
    validator       — optional callable(str) -> (value, error_msg|None)
    default         — value used when stat is unset (None = unset/blank)
    editable        — False for display-only fields (computed stats, etc.)
    """
    key: str
    label: str
    short: str
    stat_type: str = 'int'
    section: str = 'other'
    required_on_create: bool = False
    validator: Optional[Callable] = None
    default: Any = None
    editable: bool = True


class RulesetBase(ABC):
    """
    Abstract base class for all rulesets.

    Subclasses must set class-level attributes:
        RULESET_ID        str   — machine key, slug-safe, no spaces (e.g. "dnd35")
        FULL_NAME         str   — human display name (e.g. "Dungeons & Dragons 3.5")
        VERSION           str   — ruleset version string (e.g. "1.0")
        PARENT_RULESET_ID str|None — parent ruleset ID for field inheritance
        CARD_LAYOUT       str   — layout key: "dnd", "coc", or "generic"
    """

    RULESET_ID: str = ''
    FULL_NAME: str = ''
    VERSION: str = '1.0'
    PARENT_RULESET_ID: Optional[str] = None
    CARD_LAYOUT: str = 'generic'

    @abstractmethod
    def own_fields(self) -> list[FieldDef]:
        """
        Fields defined BY THIS ruleset, not inherited from a parent.
        The loader merges parent fields + own_fields() to produce all_fields().
        """

    def all_fields(self) -> list[FieldDef]:
        """
        All fields for this ruleset, including inherited parent fields.
        Override only if you need non-standard merging.
        """
        return list(self.own_fields())

    def creation_fields(self) -> list[FieldDef]:
        """Fields that are prompted during character creation (required_on_create=True)."""
        return [f for f in self.all_fields() if f.required_on_create]

    def validate_stat(self, key: str, raw: str) -> tuple[Any, Optional[str]]:
        """
        Validate and coerce a raw string value for a given stat key.
        Returns (coerced_value, None) on success, (None, error_message) on failure.
        """
        fd = self._field_map().get(key)
        if fd is None:
            return raw, None
        if fd.validator:
            return fd.validator(raw)
        if fd.stat_type == 'int':
            try:
                return int(raw), None
            except (ValueError, TypeError):
                return None, f'{fd.label} must be an integer'
        return raw, None

    def compute_derived(self, stats: dict) -> dict:
        """
        Given current stats dict, return derived/computed stats.
        These are NOT stored — computed fresh each display.
        Default: empty (no derived stats).
        """
        return {}

    def field_sections(self) -> dict[str, list[FieldDef]]:
        """Returns fields grouped by section, in canonical section order."""
        groups: dict[str, list[FieldDef]] = {s: [] for s in SECTIONS}
        for f in self.all_fields():
            groups.setdefault(f.section, []).append(f)
        return {s: fields for s, fields in groups.items() if fields}

    def _field_map(self) -> dict[str, FieldDef]:
        return {f.key: f for f in self.all_fields()}

    def __repr__(self):
        return f'<Ruleset {self.RULESET_ID!r} {self.FULL_NAME!r}>'
