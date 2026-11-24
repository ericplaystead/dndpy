"""
D&D 3.5 Subclass ruleset.
Inherits all D&D 3.5 fields. Add subclass-specific fields here as needed.
"""
from dndpy.rulesets.base import FieldDef
from dndpy.rulesets.dnd35 import DnD35Ruleset
from dndpy.utils.validators import validate_nonempty, validate_nonneg_int


class DnD35SubRuleset(DnD35Ruleset):
    RULESET_ID = 'dnd35sub'
    FULL_NAME = 'Dungeons & Dragons 3.5 (Subclass)'
    VERSION = '1.0'
    PARENT_RULESET_ID = 'dnd35'
    CARD_LAYOUT = 'dnd'

    def own_fields(self) -> list[FieldDef]:
        parent_fields = super().own_fields()
        # Add subclass-specific fields after the parent set
        subclass_fields = [
            FieldDef('subclass',        'Subclass',         'Sub',    'text', 'identity',  False, validate_nonempty),
            FieldDef('prestige_class',  'Prestige Class',   'Prest',  'text', 'identity',  False, validate_nonempty),
            FieldDef('spell_slots_1',   'Spell Slots (1st)',  'SS1',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_2',   'Spell Slots (2nd)',  'SS2',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_3',   'Spell Slots (3rd)',  'SS3',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_4',   'Spell Slots (4th)',  'SS4',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_5',   'Spell Slots (5th)',  'SS5',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_6',   'Spell Slots (6th)',  'SS6',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_7',   'Spell Slots (7th)',  'SS7',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_8',   'Spell Slots (8th)',  'SS8',  'int',  'condition', False, validate_nonneg_int),
            FieldDef('spell_slots_9',   'Spell Slots (9th)',  'SS9',  'int',  'condition', False, validate_nonneg_int),
        ]
        return parent_fields + subclass_fields
