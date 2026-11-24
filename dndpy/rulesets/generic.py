"""
Generic / fallback ruleset.
Minimal stat block: identity + core ability scores.
Use as a starting point for custom rulesets.
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import validate_nonempty, validate_int, validate_nonneg_int


class GenericRuleset(RulesetBase):
    RULESET_ID = 'generic'
    FULL_NAME = 'Generic'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'generic'

    def own_fields(self) -> list[FieldDef]:
        return [
            FieldDef('name',        'Name',          'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',    'Campaign',      'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('class_',      'Class',         'Class', 'text', 'identity', True,  validate_nonempty),
            FieldDef('level',       'Level',         'Lvl',   'int',  'identity', True,  validate_nonneg_int),
            FieldDef('race',        'Race',          'Race',  'text', 'identity', False, validate_nonempty),
            FieldDef('alignment',   'Alignment',     'Align', 'text', 'identity', False),
            FieldDef('gender',      'Gender',        'Sex',   'text', 'identity', False),

            FieldDef('strength',     'Strength',     'STR', 'int', 'ability', True,  validate_int),
            FieldDef('dexterity',    'Dexterity',    'DEX', 'int', 'ability', True,  validate_int),
            FieldDef('constitution', 'Constitution', 'CON', 'int', 'ability', True,  validate_int),
            FieldDef('intelligence', 'Intelligence', 'INT', 'int', 'ability', True,  validate_int),
            FieldDef('wisdom',       'Wisdom',       'WIS', 'int', 'ability', True,  validate_int),
            FieldDef('charisma',     'Charisma',     'CHA', 'int', 'ability', True,  validate_int),

            FieldDef('hit_points',     'Hit Points',     'HP',  'int', 'condition', True,  validate_nonneg_int),
            FieldDef('hit_points_max', 'Max Hit Points', 'MaxHP','int','condition', True,  validate_nonneg_int),
        ]
