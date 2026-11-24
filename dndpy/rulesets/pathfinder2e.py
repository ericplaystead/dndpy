"""
Pathfinder 2nd Edition ruleset.
Based on the Pathfinder 2e Core Rulebook / Remaster (2023).

Key differences from PF1/DnD3.5:
  - No BAB, CMB, CMD, Touch AC, or Flat-Foot AC as tracked stats
  - Proficiency system (Untrained/Trained/Expert/Master/Legendary)
  - Three-action economy (tracked in play, not on sheet)
  - Hero Points (0–3) instead of action points
  - Class DC instead of caster level
  - Ancestries instead of races; Heritages are subtype of ancestry
  - Alignment removed in the Remaster (kept as optional text for older tables)
  - Skills: 16 core skills, all proficiency-based

Stat tracking approach: store final total bonuses rather than decomposing
proficiency rank + ability mod + item bonus — the full breakdown lives on
the paper sheet. The DB records the totals that matter during play.
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int, validate_choice
)

CLASSES = [
    'alchemist', 'barbarian', 'bard', 'champion', 'cleric', 'druid',
    'fighter', 'gunslinger', 'inventor', 'investigator', 'kineticist',
    'magus', 'monk', 'oracle', 'psychic', 'ranger', 'rogue', 'sorcerer',
    'summoner', 'swashbuckler', 'thaumaturge', 'witch', 'wizard',
]

ANCESTRIES = [
    'dwarf', 'elf', 'gnome', 'goblin', 'halfling', 'human',
    'half-elf', 'half-orc', 'orc', 'leshy', 'lizardfolk', 'ratfolk',
    'tengu', 'catfolk', 'fetchling', 'fleshwarp', 'grippli', 'kitsune',
    'kobold', 'shoony', 'sprite', 'strix',
]

SIZES = ['tiny', 'small', 'medium', 'large', 'huge', 'gargantuan']

ALIGNMENTS = [
    'lawful good', 'neutral good', 'chaotic good',
    'lawful neutral', 'true neutral', 'chaotic neutral',
    'lawful evil', 'neutral evil', 'chaotic evil',
]


def _ability_mod(score: int) -> int:
    return (score - 10) // 2


class Pathfinder2eRuleset(RulesetBase):
    RULESET_ID = 'pf2e'
    FULL_NAME = 'Pathfinder 2e'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'dnd'

    def own_fields(self) -> list[FieldDef]:
        return [
            # ── Identity ─────────────────────────────────────────────────────
            FieldDef('name',        'Name',        'Name',    'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',    'Campaign',    'Camp',    'text', 'identity', False, validate_nonempty),
            FieldDef('class_',      'Class',       'Class',   'text', 'identity', True,  validate_choice(CLASSES)),
            FieldDef('level',       'Level',       'Lvl',     'int',  'identity', True,  validate_positive_int),
            FieldDef('ancestry',    'Ancestry',    'Anc',     'text', 'identity', True,  validate_choice(ANCESTRIES)),
            FieldDef('heritage',    'Heritage',    'Hrtg',    'text', 'identity', False, validate_nonempty),
            FieldDef('background',  'Background',  'BG',      'text', 'identity', False, validate_nonempty),
            FieldDef('size',        'Size',        'Size',    'text', 'identity', False,
                     validate_choice(SIZES), default='medium'),
            FieldDef('deity',       'Deity',       'Deity',   'text', 'identity', False),
            FieldDef('alignment',   'Alignment',   'Align',   'text', 'identity', False,
                     validate_choice(ALIGNMENTS)),  # optional; removed in Remaster but still common
            FieldDef('languages',   'Languages',   'Lang',    'text', 'other',    False),
            FieldDef('edicts',      'Edicts',      'Edcts',   'text', 'other',    False),
            FieldDef('anathema',    'Anathema',    'Anath',   'text', 'other',    False),

            # ── Ability Scores ────────────────────────────────────────────────
            FieldDef('strength',     'Strength',     'STR', 'int', 'ability', True, validate_int),
            FieldDef('dexterity',    'Dexterity',    'DEX', 'int', 'ability', True, validate_int),
            FieldDef('constitution', 'Constitution', 'CON', 'int', 'ability', True, validate_int),
            FieldDef('intelligence', 'Intelligence', 'INT', 'int', 'ability', True, validate_int),
            FieldDef('wisdom',       'Wisdom',       'WIS', 'int', 'ability', True, validate_int),
            FieldDef('charisma',     'Charisma',     'CHA', 'int', 'ability', True, validate_int),

            # ── Combat ───────────────────────────────────────────────────────
            FieldDef('hit_points',      'Hit Points',      'HP',      'int', 'combat', True,  validate_nonneg_int),
            FieldDef('hit_points_max',  'Max Hit Points',  'MaxHP',   'int', 'combat', True,  validate_positive_int),
            FieldDef('temp_hit_points', 'Temp Hit Points', 'Temp',    'int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('armor_class',     'Armor Class',     'AC',      'int', 'combat', False, validate_int, default=10),
            FieldDef('speed',           'Speed (ft)',       'Spd',     'int', 'combat', False, validate_positive_int, default=25),
            FieldDef('initiative',      'Initiative',      'Init',    'int', 'combat', False, validate_int, default=0),
            FieldDef('perception',      'Perception',      'Perc',    'int', 'combat', False, validate_int, default=0),
            FieldDef('class_dc',        'Class DC',        'ClsDC',   'int', 'combat', False, validate_int, default=10),
            FieldDef('hero_points',     'Hero Points',     'Hero',    'int', 'combat', False, validate_nonneg_int, default=1),
            FieldDef('dying',           'Dying',           'Dying',   'int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('wounded',         'Wounded',         'Wnd',     'int', 'combat', False, validate_nonneg_int, default=0),
            FieldDef('drained',         'Drained',         'Drn',     'int', 'combat', False, validate_nonneg_int, default=0),

            # ── Saving Throws (total modifier) ───────────────────────────────
            FieldDef('save_fortitude', 'Fortitude', 'Fort', 'int', 'saves', False, validate_int, default=0),
            FieldDef('save_reflex',    'Reflex',    'Ref',  'int', 'saves', False, validate_int, default=0),
            FieldDef('save_will',      'Will',      'Will', 'int', 'saves', False, validate_int, default=0),

            # ── Skills (total modifiers including proficiency + ability) ──────
            FieldDef('acrobatics',   'Acrobatics',   'Acro',  'int', 'skills', False, validate_int),
            FieldDef('arcana',       'Arcana',       'Arca',  'int', 'skills', False, validate_int),
            FieldDef('athletics',    'Athletics',    'Athl',  'int', 'skills', False, validate_int),
            FieldDef('crafting',     'Crafting',     'Crft',  'int', 'skills', False, validate_int),
            FieldDef('deception',    'Deception',    'Dcpt',  'int', 'skills', False, validate_int),
            FieldDef('diplomacy',    'Diplomacy',    'Dipl',  'int', 'skills', False, validate_int),
            FieldDef('intimidation', 'Intimidation', 'Intm',  'int', 'skills', False, validate_int),
            FieldDef('medicine',     'Medicine',     'Medi',  'int', 'skills', False, validate_int),
            FieldDef('nature',       'Nature',       'Natr',  'int', 'skills', False, validate_int),
            FieldDef('occultism',    'Occultism',    'Oclt',  'int', 'skills', False, validate_int),
            FieldDef('performance',  'Performance',  'Perf',  'int', 'skills', False, validate_int),
            FieldDef('religion',     'Religion',     'Reli',  'int', 'skills', False, validate_int),
            FieldDef('society',      'Society',      'Soct',  'int', 'skills', False, validate_int),
            FieldDef('stealth',      'Stealth',      'Stlh',  'int', 'skills', False, validate_int),
            FieldDef('survival',     'Survival',     'Surv',  'int', 'skills', False, validate_int),
            FieldDef('thievery',     'Thievery',     'Thvr',  'int', 'skills', False, validate_int),
            FieldDef('lore1_name',   'Lore 1 (name)', 'Lor1', 'text','skills', False),
            FieldDef('lore1_bonus',  'Lore 1 (bonus)','L1Bn', 'int', 'skills', False, validate_int),
            FieldDef('lore2_name',   'Lore 2 (name)', 'Lor2', 'text','skills', False),
            FieldDef('lore2_bonus',  'Lore 2 (bonus)','L2Bn', 'int', 'skills', False, validate_int),

            # ── Spellcasting / Focus ──────────────────────────────────────────
            FieldDef('spell_dc',        'Spell DC',        'SpDC', 'int', 'condition', False, validate_int),
            FieldDef('spell_attack',    'Spell Attack',    'SpAtk','int', 'condition', False, validate_int),
            FieldDef('focus_points',    'Focus Points',    'FP',   'int', 'condition', False, validate_nonneg_int, default=0),
            FieldDef('focus_points_max','Max Focus Points','MaxFP','int', 'condition', False, validate_nonneg_int, default=0),
            FieldDef('resonance',       'Resonance',       'Res',  'int', 'condition', False, validate_nonneg_int),

            # ── Condition / Progression ───────────────────────────────────────
            FieldDef('experience',      'Experience',      'XP',   'int', 'condition', False, validate_nonneg_int, default=0),
            FieldDef('spell_resist',    'Spell Resistance','SR',   'int', 'condition', False, validate_nonneg_int),

            # ── Other / Backstory ─────────────────────────────────────────────
            FieldDef('feats',   'Notable Feats',   'Feats', 'text', 'other', False),
            FieldDef('notes',   'Notes',           'Notes', 'text', 'other', False),
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
