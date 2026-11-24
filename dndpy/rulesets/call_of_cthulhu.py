"""
Call of Cthulhu ruleset (7th Edition).
Completely independent stat system — no D&D ability score inheritance.
Includes Sanity, Magic Points, Luck, and Investigator-specific attributes.
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int
)


def _idea_from_int(stats: dict) -> int:
    v = stats.get('intelligence')
    return v if v is not None else 0


class CallOfCthulhuRuleset(RulesetBase):
    RULESET_ID = 'coc'
    FULL_NAME = 'Call of Cthulhu'
    VERSION = '7th Edition'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'coc'

    def own_fields(self) -> list[FieldDef]:
        return [
            # --- Identity / Investigator Info ---
            FieldDef('name',        'Name',        'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('full_name',   'Full Name',   'Full',  'text', 'identity', False, validate_nonempty),
            FieldDef('campaign',    'Campaign',    'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('occupation',  'Occupation',  'Occ',   'text', 'identity', True,  validate_nonempty),
            FieldDef('nationality', 'Nationality', 'Natl',  'text', 'identity', False, validate_nonempty),
            FieldDef('residence',   'Residence',   'Res',   'text', 'identity', False, validate_nonempty),
            FieldDef('birthplace',  'Birthplace',  'Birth', 'text', 'identity', False, validate_nonempty),
            FieldDef('age',         'Age',         'Age',   'int',  'identity', True,  validate_positive_int),
            FieldDef('sex',         'Sex',         'Sex',   'text', 'identity', False, validate_nonempty),

            # --- Characteristics ---
            FieldDef('strength',     'Strength',     'STR', 'int', 'ability', True, validate_positive_int),
            FieldDef('dexterity',    'Dexterity',    'DEX', 'int', 'ability', True, validate_positive_int),
            FieldDef('intelligence', 'Intelligence', 'INT', 'int', 'ability', True, validate_positive_int),
            FieldDef('constitution', 'Constitution', 'CON', 'int', 'ability', True, validate_positive_int),
            FieldDef('appearance',   'Appearance',   'APP', 'int', 'ability', True, validate_positive_int),
            FieldDef('power',        'Power',        'POW', 'int', 'ability', True, validate_positive_int),
            FieldDef('size',         'Size',         'SIZ', 'int', 'ability', True, validate_positive_int),
            FieldDef('education',    'Education',    'EDU', 'int', 'ability', True, validate_positive_int),

            # --- Condition ---
            FieldDef('hit_points',     'Hit Points',     'HP',    'int', 'condition', True,  validate_positive_int),
            FieldDef('hit_points_max', 'Max Hit Points', 'MaxHP', 'int', 'condition', False, validate_positive_int),
            FieldDef('magic_points',   'Magic Points',   'MP',    'int', 'condition', True,  validate_nonneg_int),
            FieldDef('magic_points_max','Max Magic Points','MaxMP','int', 'condition', False, validate_nonneg_int),
            FieldDef('sanity',         'Sanity',         'SAN',   'int', 'condition', True,  validate_nonneg_int),
            FieldDef('sanity_max',     'Max Sanity',     'MaxSAN','int', 'condition', False, validate_nonneg_int),
            FieldDef('luck',           'Luck',           'LCK',   'int', 'condition', True,  validate_positive_int),
        ]

    def compute_derived(self, stats: dict) -> dict:
        derived = {}
        # Idea = INT
        if stats.get('intelligence') is not None:
            derived['idea'] = stats['intelligence']
        # Know = EDU
        if stats.get('education') is not None:
            derived['know'] = stats['education']
        # Damage Bonus from STR + SIZ
        str_ = stats.get('strength')
        siz = stats.get('size')
        if str_ is not None and siz is not None:
            total = int(str_) + int(siz)
            if total <= 12:
                derived['damage_bonus'] = '-1d6'
            elif total <= 16:
                derived['damage_bonus'] = '-1d4'
            elif total <= 24:
                derived['damage_bonus'] = 'None'
            elif total <= 32:
                derived['damage_bonus'] = '+1d4'
            else:
                derived['damage_bonus'] = '+1d6'
        return derived
