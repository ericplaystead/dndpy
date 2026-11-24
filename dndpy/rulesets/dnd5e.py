"""
Dungeons & Dragons 5th Edition ruleset (Wizards of the Coast, 2014).

Key differences from DnD 3.5 / Pathfinder:
  - Proficiency bonus (+2 to +6) replaces per-skill ranks
  - Advantage/disadvantage system replaces most situational modifiers
  - Twelve classes including Warlock (new vs. 3.5)
  - Races include Dragonborn and Tiefling as core options
  - Inspiration (binary flag, awarded by DM)
  - Death saving throws (three successes or failures)
  - Exhaustion levels (1–6, each with escalating effects)
  - Short rest / long rest recovery tracked by HD expended
  - Spell slots tracked as current/max per slot level (1–9)
  - Backgrounds replace starting packages; each grants proficiencies and a feature
  - No Touch AC or Flat-Foot AC; one AC value
  - Skills: 18 skills tied to specific abilities
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int, validate_choice
)

CLASSES = [
    'barbarian', 'bard', 'cleric', 'druid', 'fighter', 'monk',
    'paladin', 'ranger', 'rogue', 'sorcerer', 'warlock', 'wizard',
]

RACES = [
    'dragonborn', 'dwarf', 'elf', 'gnome', 'half-elf', 'half-orc',
    'halfling', 'human', 'tiefling',
]

SIZES = ['tiny', 'small', 'medium', 'large', 'huge', 'gargantuan']

ALIGNMENTS = [
    'lawful good', 'neutral good', 'chaotic good',
    'lawful neutral', 'true neutral', 'chaotic neutral',
    'lawful evil', 'neutral evil', 'chaotic evil',
    'unaligned',
]

GENDERS = ['male', 'female', 'other']

BACKGROUNDS = [
    'acolyte', 'charlatan', 'criminal', 'entertainer', 'folk hero',
    'guild artisan', 'hermit', 'noble', 'outlander', 'sage',
    'sailor', 'soldier', 'urchin',
]


def _ability_mod(score: int) -> int:
    return (score - 10) // 2


def _proficiency_bonus(level: int) -> int:
    """5e proficiency bonus: +2 at levels 1–4, scaling to +6 at 17–20."""
    return (level - 1) // 4 + 2


class DnD5eRuleset(RulesetBase):
    RULESET_ID = 'dnd5e'
    FULL_NAME = 'Dungeons & Dragons 5e'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'dnd'

    def own_fields(self) -> list[FieldDef]:
        return [
            # ── Identity ─────────────────────────────────────────────────────
            FieldDef('name',       'Name',       'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',   'Campaign',   'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('class_',     'Class',      'Class', 'text', 'identity', True,  validate_choice(CLASSES)),
            FieldDef('subclass',   'Subclass',   'Sub',   'text', 'identity', False, validate_nonempty),
            FieldDef('level',      'Level',      'Lvl',   'int',  'identity', True,  validate_positive_int),
            FieldDef('race',       'Race',       'Race',  'text', 'identity', True,  validate_choice(RACES)),
            FieldDef('background', 'Background', 'BG',    'text', 'identity', True,  validate_choice(BACKGROUNDS)),
            FieldDef('alignment',  'Alignment',  'Align', 'text', 'identity', False, validate_choice(ALIGNMENTS)),
            FieldDef('gender',     'Gender',     'Sex',   'text', 'identity', False, validate_choice(GENDERS)),
            FieldDef('size',       'Size',       'Size',  'text', 'identity', False,
                     validate_choice(SIZES), default='medium'),
            FieldDef('deity',      'Deity',      'Deity', 'text', 'identity', False),
            FieldDef('experience', 'Experience', 'XP',    'int',  'identity', False, validate_nonneg_int, default=0),

            # ── Ability Scores ────────────────────────────────────────────────
            FieldDef('strength',     'Strength',     'STR', 'int', 'ability', True, validate_int),
            FieldDef('dexterity',    'Dexterity',    'DEX', 'int', 'ability', True, validate_int),
            FieldDef('constitution', 'Constitution', 'CON', 'int', 'ability', True, validate_int),
            FieldDef('intelligence', 'Intelligence', 'INT', 'int', 'ability', True, validate_int),
            FieldDef('wisdom',       'Wisdom',       'WIS', 'int', 'ability', True, validate_int),
            FieldDef('charisma',     'Charisma',     'CHA', 'int', 'ability', True, validate_int),

            # ── Combat ───────────────────────────────────────────────────────
            FieldDef('hit_points',       'Hit Points',       'HP',    'int', 'combat', True,  validate_nonneg_int),
            FieldDef('hit_points_max',   'Max Hit Points',   'MaxHP', 'int', 'combat', True,  validate_positive_int),
            FieldDef('temp_hit_points',  'Temp Hit Points',  'Temp',  'int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('hit_dice',         'Hit Dice Remaining','HD',   'int', 'combat', False, validate_nonneg_int),
            FieldDef('armor_class',      'Armor Class',      'AC',    'int', 'combat', False, validate_int, default=10),
            FieldDef('speed',            'Speed (ft)',        'Spd',   'int', 'combat', False, validate_positive_int, default=30),
            FieldDef('initiative',       'Initiative',       'Init',  'int', 'combat', False, validate_int, default=0),
            FieldDef('proficiency_bonus','Proficiency Bonus','Prof',  'int', 'combat', False, validate_positive_int, default=2),
            FieldDef('inspiration',      'Inspiration',      'Insp',  'int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('passive_perception','Passive Perception','PPerc','int', 'combat', False, validate_int),
            # Death saves: track successes and failures separately (0–3)
            FieldDef('death_save_success','Death Save Successes','DS+','int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('death_save_failure','Death Save Failures', 'DS-','int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('exhaustion',       'Exhaustion Level', 'Exh',   'int', 'combat', False, validate_nonneg_int, default=0),

            # ── Saving Throws (total modifier) ───────────────────────────────
            FieldDef('save_strength',     'Strength Save',     'StrSv', 'int', 'saves', False, validate_int),
            FieldDef('save_dexterity',    'Dexterity Save',    'DexSv', 'int', 'saves', False, validate_int),
            FieldDef('save_constitution', 'Constitution Save', 'ConSv', 'int', 'saves', False, validate_int),
            FieldDef('save_intelligence', 'Intelligence Save', 'IntSv', 'int', 'saves', False, validate_int),
            FieldDef('save_wisdom',       'Wisdom Save',       'WisSv', 'int', 'saves', False, validate_int),
            FieldDef('save_charisma',     'Charisma Save',     'ChaSv', 'int', 'saves', False, validate_int),

            # ── Skills (total modifier) ───────────────────────────────────────
            # STR
            FieldDef('athletics',     'Athletics',     'Athl', 'int', 'skills', False, validate_int),
            # DEX
            FieldDef('acrobatics',    'Acrobatics',    'Acro', 'int', 'skills', False, validate_int),
            FieldDef('sleight_of_hand','Sleight of Hand','SoH','int', 'skills', False, validate_int),
            FieldDef('stealth',       'Stealth',       'Stlh', 'int', 'skills', False, validate_int),
            # INT
            FieldDef('arcana',        'Arcana',        'Arca', 'int', 'skills', False, validate_int),
            FieldDef('history',       'History',       'Hist', 'int', 'skills', False, validate_int),
            FieldDef('investigation', 'Investigation', 'Invs', 'int', 'skills', False, validate_int),
            FieldDef('nature',        'Nature',        'Natr', 'int', 'skills', False, validate_int),
            FieldDef('religion',      'Religion',      'Reli', 'int', 'skills', False, validate_int),
            # WIS
            FieldDef('animal_handling','Animal Handling','AnHn','int', 'skills', False, validate_int),
            FieldDef('insight',       'Insight',       'Insg', 'int', 'skills', False, validate_int),
            FieldDef('medicine',      'Medicine',      'Medi', 'int', 'skills', False, validate_int),
            FieldDef('perception',    'Perception',    'Perc', 'int', 'skills', False, validate_int),
            FieldDef('survival',      'Survival',      'Surv', 'int', 'skills', False, validate_int),
            # CHA
            FieldDef('deception',     'Deception',     'Dcpt', 'int', 'skills', False, validate_int),
            FieldDef('intimidation',  'Intimidation',  'Intm', 'int', 'skills', False, validate_int),
            FieldDef('performance',   'Performance',   'Perf', 'int', 'skills', False, validate_int),
            FieldDef('persuasion',    'Persuasion',    'Pers', 'int', 'skills', False, validate_int),

            # ── Spell Slots (current/max as text, e.g. "3/4") ─────────────────
            FieldDef('spell_dc',    'Spell Save DC',   'SpDC', 'int',  'condition', False, validate_int),
            FieldDef('spell_atk',   'Spell Attack',    'SpAtk','int',  'condition', False, validate_int),
            FieldDef('spell_s1',    'Spell Slots Lvl 1','Sp1', 'text', 'condition', False),
            FieldDef('spell_s2',    'Spell Slots Lvl 2','Sp2', 'text', 'condition', False),
            FieldDef('spell_s3',    'Spell Slots Lvl 3','Sp3', 'text', 'condition', False),
            FieldDef('spell_s4',    'Spell Slots Lvl 4','Sp4', 'text', 'condition', False),
            FieldDef('spell_s5',    'Spell Slots Lvl 5','Sp5', 'text', 'condition', False),
            FieldDef('spell_s6',    'Spell Slots Lvl 6','Sp6', 'text', 'condition', False),
            FieldDef('spell_s7',    'Spell Slots Lvl 7','Sp7', 'text', 'condition', False),
            FieldDef('spell_s8',    'Spell Slots Lvl 8','Sp8', 'text', 'condition', False),
            FieldDef('spell_s9',    'Spell Slots Lvl 9','Sp9', 'text', 'condition', False),

            # ── Other / Backstory ─────────────────────────────────────────────
            FieldDef('languages',   'Languages',       'Lang',  'text', 'other', False),
            FieldDef('features',    'Class Features',  'Feats', 'text', 'other', False),
            FieldDef('equipment',   'Equipment',       'Equip', 'text', 'other', False),
            FieldDef('notes',       'Notes',           'Notes', 'text', 'other', False),
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

        # Proficiency bonus from level (if not manually overridden)
        if 'proficiency_bonus' not in stats:
            level = stats.get('level')
            if level is not None:
                try:
                    derived['proficiency_bonus'] = _proficiency_bonus(int(level))
                except (ValueError, TypeError):
                    pass

        # Passive perception = 10 + WIS mod (if wisdom is set and not overridden)
        if 'passive_perception' not in stats:
            wis_mod = derived.get('wis_mod')
            if wis_mod is not None:
                derived['passive_perception'] = 10 + wis_mod

        return derived
