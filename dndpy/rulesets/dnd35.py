"""
Dungeons & Dragons 3.5 Edition ruleset.
Extends generic with full D&D stat block: combat, saves, AC breakdown, skills.
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int, validate_choice
)

ALIGNMENTS = [
    'lawful good', 'neutral good', 'chaotic good',
    'lawful neutral', 'true neutral', 'chaotic neutral',
    'lawful evil', 'neutral evil', 'chaotic evil',
]
CLASSES = [
    'barbarian', 'bard', 'cleric', 'druid', 'fighter', 'monk',
    'paladin', 'ranger', 'rogue', 'sorcerer', 'wizard',
]
RACES = ['human', 'elf', 'dwarf', 'gnome', 'half-elf', 'half-orc', 'halfling']
SIZES = ['fine', 'diminutive', 'tiny', 'small', 'medium', 'large', 'huge', 'gargantuan', 'colossal']
GENDERS = ['male', 'female', 'other']


def _ability_mod(score: int) -> int:
    return (score - 10) // 2


class DnD35Ruleset(RulesetBase):
    RULESET_ID = 'dnd35'
    FULL_NAME = 'Dungeons & Dragons 3.5'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'dnd'

    def own_fields(self) -> list[FieldDef]:
        return [
            # --- Identity ---
            FieldDef('name',       'Name',      'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',   'Campaign',  'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('class_',     'Class',     'Class', 'text', 'identity', True,
                     validate_choice(CLASSES)),
            FieldDef('level',      'Level',     'Lvl',   'int',  'identity', True,  validate_positive_int),
            FieldDef('race',       'Race',      'Race',  'text', 'identity', True,
                     validate_choice(RACES)),
            FieldDef('alignment',  'Alignment', 'Align', 'text', 'identity', True,
                     validate_choice(ALIGNMENTS)),
            FieldDef('gender',     'Gender',    'Sex',   'text', 'identity', False,
                     validate_choice(GENDERS)),
            FieldDef('size',       'Size',      'Size',  'text', 'identity', False,
                     validate_choice(SIZES), default='medium'),
            FieldDef('deity',      'Deity',     'Deity', 'text', 'identity', False),

            # --- Ability Scores ---
            FieldDef('strength',     'Strength',     'STR', 'int', 'ability', True, validate_int),
            FieldDef('dexterity',    'Dexterity',    'DEX', 'int', 'ability', True, validate_int),
            FieldDef('constitution', 'Constitution', 'CON', 'int', 'ability', True, validate_int),
            FieldDef('intelligence', 'Intelligence', 'INT', 'int', 'ability', True, validate_int),
            FieldDef('wisdom',       'Wisdom',       'WIS', 'int', 'ability', True, validate_int),
            FieldDef('charisma',     'Charisma',     'CHA', 'int', 'ability', True, validate_int),

            # --- Combat ---
            FieldDef('hit_points',     'Hit Points',     'HP',    'int', 'combat', True,  validate_nonneg_int),
            FieldDef('hit_points_max', 'Max Hit Points', 'MaxHP', 'int', 'combat', True,  validate_positive_int),
            FieldDef('armor_class',    'Armor Class',    'AC',    'int', 'combat', False, validate_int, default=10),
            FieldDef('touch_ac',       'Touch AC',       'Touch', 'int', 'combat', False, validate_int, default=10),
            FieldDef('flatfoot_ac',    'Flat-Foot AC',   'FF',    'int', 'combat', False, validate_int, default=10),
            FieldDef('initiative',     'Initiative',     'Init',  'int', 'combat', False, validate_int, default=0),
            FieldDef('speed',          'Speed (ft)',      'Spd',   'int', 'combat', False, validate_int, default=30),
            FieldDef('base_attack',    'Base Attack Bonus','BAB',  'int', 'combat', False, validate_int, default=0),
            FieldDef('cmb',            'CMB',            'CMB',   'int', 'combat', False, validate_int, default=0),
            FieldDef('cmd',            'CMD',            'CMD',   'int', 'combat', False, validate_int, default=10),

            # --- Saving Throws ---
            FieldDef('save_fortitude', 'Fortitude', 'Fort', 'int', 'saves', False, validate_int, default=0),
            FieldDef('save_reflex',    'Reflex',    'Ref',  'int', 'saves', False, validate_int, default=0),
            FieldDef('save_will',      'Will',      'Will', 'int', 'saves', False, validate_int, default=0),

            # --- Condition ---
            FieldDef('experience',     'Experience Points', 'XP',  'int', 'condition', False, validate_nonneg_int),
            FieldDef('spell_resist',   'Spell Resistance',  'SR',  'int', 'condition', False, validate_nonneg_int),
        ]

    def compute_derived(self, stats: dict) -> dict:
        derived = {}
        for key, short in [
            ('strength', 'str'), ('dexterity', 'dex'), ('constitution', 'con'),
            ('intelligence', 'int'), ('wisdom', 'wis'), ('charisma', 'cha'),
        ]:
            score = stats.get(key)
            if score is not None:
                try:
                    derived[f'{short}_mod'] = _ability_mod(int(score))
                except (ValueError, TypeError):
                    pass
        return derived
