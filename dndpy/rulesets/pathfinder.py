"""
Pathfinder ruleset.
Closely related to D&D 3.5 — inherits the full stat block and extends with
Pathfinder-specific traits (CMB/CMD already in 3.5, adds traits and mythic).
"""
from dndpy.rulesets.base import FieldDef
from dndpy.rulesets.dnd35 import DnD35Ruleset
from dndpy.utils.validators import validate_nonempty, validate_nonneg_int, validate_choice

CLASSES = [
    'alchemist', 'barbarian', 'bard', 'cavalier', 'cleric', 'druid',
    'fighter', 'gunslinger', 'inquisitor', 'magus', 'monk', 'ninja',
    'oracle', 'paladin', 'ranger', 'rogue', 'samurai', 'shaman',
    'skald', 'slayer', 'sorcerer', 'summoner', 'swashbuckler',
    'warpriest', 'witch', 'wizard',
]


class PathfinderRuleset(DnD35Ruleset):
    RULESET_ID = 'pathfinder'
    FULL_NAME = 'Pathfinder'
    VERSION = '1.0'
    PARENT_RULESET_ID = None  # sibling of dnd35, not a child
    CARD_LAYOUT = 'dnd'

    def own_fields(self) -> list[FieldDef]:
        parent_fields = super().own_fields()

        # Replace class_ validator with Pathfinder class list
        updated = []
        for f in parent_fields:
            if f.key == 'class_':
                updated.append(FieldDef(
                    f.key, f.label, f.short, f.stat_type, f.section,
                    f.required_on_create, validate_choice(CLASSES), f.default
                ))
            else:
                updated.append(f)

        pf_extra = [
            FieldDef('secondary_class',  'Secondary Class', 'Class2', 'text', 'identity',  False, validate_choice(CLASSES)),
            FieldDef('archetype',        'Archetype',       'Arch',   'text', 'identity',  False, validate_nonempty),
            FieldDef('mythic_tier',      'Mythic Tier',     'Myth',   'int',  'identity',  False, validate_nonneg_int),
            FieldDef('traits',           'Traits',          'Traits', 'text', 'other',     False),
        ]
        return updated + pf_extra
