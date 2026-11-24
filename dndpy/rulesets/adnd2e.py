"""
Advanced Dungeons & Dragons 2nd Edition ruleset (TSR, 1989).
Authors: David "Zeb" Cook et al.

Key differences from DnD 3.5 / Pathfinder:
  - Descending Armor Class (10 to -10) with THAC0 combat system
  - Five saving throw categories (PPDM, PP, RSW, BW, Spell)
  - Exceptional Strength for warriors with STR 18 (18/01–18/00)
  - Class list: Fighter, Paladin, Ranger, Mage, Illusionist, Cleric, Druid, Thief, Bard
  - Multi-class (demi-humans) and dual-class (humans) supported via free-text field
  - Non-Weapon Proficiencies (NWPs) replace skills
  - Thief skills: percentage-based abilities unique to Thief/Bard
  - Spell slots tracked per spell level (wizard 1–9, priest 1–7)
  - Proficiency slots for weapon proficiencies
  - No feats, no prestige classes, no CMB/CMD
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int, validate_choice
)

CLASSES = [
    # Warriors
    'fighter', 'paladin', 'ranger',
    # Wizards
    'mage', 'abjurer', 'conjurer', 'diviner', 'enchanter',
    'illusionist', 'invoker', 'necromancer', 'transmuter',
    # Priests
    'cleric', 'druid',
    # Rogues
    'thief', 'bard',
]

RACES = [
    'human', 'elf', 'half-elf', 'dwarf', 'gnome', 'halfling', 'half-orc',
]

ALIGNMENTS = [
    'lawful good', 'neutral good', 'chaotic good',
    'lawful neutral', 'true neutral', 'chaotic neutral',
    'lawful evil', 'neutral evil', 'chaotic evil',
]

GENDERS = ['male', 'female', 'other']

SIZES = ['tiny', 'small', 'medium', 'large', 'huge', 'gargantuan']


class ADnD2eRuleset(RulesetBase):
    RULESET_ID = 'adnd2e'
    FULL_NAME = 'AD&D 2nd Edition'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'dnd'

    def own_fields(self) -> list[FieldDef]:
        return [
            # ── Identity ─────────────────────────────────────────────────────
            FieldDef('name',       'Name',       'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',   'Campaign',   'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('class_',     'Class',      'Class', 'text', 'identity', True,  validate_choice(CLASSES)),
            # Multi-class / dual-class stored as free text, e.g. "Fighter/Mage" or "Fighter→Mage"
            FieldDef('multiclass', 'Multi/Dual Class', 'MC', 'text', 'identity', False),
            FieldDef('level',      'Level',      'Lvl',   'int',  'identity', True,  validate_positive_int),
            # Multi-class characters track separate levels, e.g. "5/5"
            FieldDef('level_detail','Level Detail','LvlD', 'text', 'identity', False),
            FieldDef('race',       'Race',       'Race',  'text', 'identity', True,  validate_choice(RACES)),
            FieldDef('alignment',  'Alignment',  'Align', 'text', 'identity', True,  validate_choice(ALIGNMENTS)),
            FieldDef('gender',     'Gender',     'Sex',   'text', 'identity', False, validate_choice(GENDERS)),
            FieldDef('size',       'Size',       'Size',  'text', 'identity', False,
                     validate_choice(SIZES), default='medium'),
            FieldDef('deity',      'Deity',      'Deity', 'text', 'identity', False),
            FieldDef('age',        'Age',        'Age',   'int',  'identity', False, validate_positive_int),
            FieldDef('experience', 'Experience', 'XP',    'int',  'identity', False, validate_nonneg_int, default=0),
            # For multi-class; XP per class tracked as free text
            FieldDef('experience_detail', 'XP Detail', 'XPD', 'text', 'identity', False),

            # ── Ability Scores ────────────────────────────────────────────────
            FieldDef('strength',     'Strength',     'STR', 'int', 'ability', True, validate_int),
            # Exceptional Strength: warriors with STR 18 may roll d100 for 18/xx.
            # Stored as text to hold "18/75", "18/00" etc. (blank for non-warriors or STR < 18)
            FieldDef('strength_exc', 'Str Exceptional', 'STRx', 'text', 'ability', False),
            FieldDef('dexterity',    'Dexterity',    'DEX', 'int', 'ability', True, validate_int),
            FieldDef('constitution', 'Constitution', 'CON', 'int', 'ability', True, validate_int),
            FieldDef('intelligence', 'Intelligence', 'INT', 'int', 'ability', True, validate_int),
            FieldDef('wisdom',       'Wisdom',       'WIS', 'int', 'ability', True, validate_int),
            FieldDef('charisma',     'Charisma',     'CHA', 'int', 'ability', True, validate_int),

            # ── Combat ───────────────────────────────────────────────────────
            # 2e uses THAC0: roll d20, add target's AC; result must meet or exceed THAC0.
            # Lower THAC0 is better. Warriors start at 20 and descend fastest.
            FieldDef('hit_points',     'Hit Points',     'HP',    'int', 'combat', True,  validate_nonneg_int),
            FieldDef('hit_points_max', 'Max Hit Points', 'MaxHP', 'int', 'combat', True,  validate_positive_int),
            # Descending AC: 10 (unarmored) down to -10 (powerful magic armor)
            FieldDef('armor_class',    'Armor Class',    'AC',    'int', 'combat', False, validate_int, default=10),
            FieldDef('ac_rear',        'Rear AC',        'RrAC',  'int', 'combat', False, validate_int),
            FieldDef('thac0',          'THAC0',          'THAC0', 'int', 'combat', False, validate_int, default=20),
            FieldDef('attack_adj',     'Attack Adjustment', 'AtkAdj', 'int', 'combat', False, validate_int, default=0),
            FieldDef('damage_adj',     'Damage Adjustment', 'DmgAdj', 'int', 'combat', False, validate_int, default=0),
            FieldDef('speed',          'Movement (yds/rd)', 'MV',  'int', 'combat', False, validate_positive_int, default=12),
            FieldDef('initiative_adj', 'Initiative Adj', 'Init',  'int', 'combat', False, validate_int, default=0),
            FieldDef('num_attacks',    'Attacks/Round',  'Atk/Rd','text','combat', False, default='1'),

            # ── Saving Throws ────────────────────────────────────────────────
            # Roll d20, meet or exceed the number to succeed. Lower is better.
            FieldDef('save_ppdm', 'Paralysis, Poison, Death Magic', 'PPDM', 'int', 'saves', False, validate_int),
            FieldDef('save_pp',   'Petrification / Polymorph',      'PP',   'int', 'saves', False, validate_int),
            FieldDef('save_rsw',  'Rod, Staff, or Wand',            'RSW',  'int', 'saves', False, validate_int),
            FieldDef('save_bw',   'Breath Weapon',                  'BW',   'int', 'saves', False, validate_int),
            FieldDef('save_spell','Spell',                          'Spell','int', 'saves', False, validate_int),

            # ── Thief Skills (percentage) ─────────────────────────────────────
            # Used by Thief and Bard. Stored as integers (0–100+).
            # Non-thieves leave these blank.
            FieldDef('ts_pick_pockets',    'Pick Pockets',      'PP%',  'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_open_locks',      'Open Locks',        'OL%',  'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_find_traps',      'Find/Remove Traps', 'FRT%', 'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_move_silently',   'Move Silently',     'MS%',  'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_hide_in_shadows', 'Hide in Shadows',   'HiS%', 'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_detect_noise',    'Detect Noise',      'DN%',  'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_climb_walls',     'Climb Walls',       'CW%',  'int', 'skills', False, validate_nonneg_int),
            FieldDef('ts_read_languages',  'Read Languages',    'RL%',  'int', 'skills', False, validate_nonneg_int),

            # ── Spell Slots (Wizard 1–9, Priest 1–7) ─────────────────────────
            # Stored as "current/max" free text, e.g. "3/4", to track expended slots.
            FieldDef('spell_w1', 'Wizard Spells Lvl 1', 'W1', 'text', 'condition', False),
            FieldDef('spell_w2', 'Wizard Spells Lvl 2', 'W2', 'text', 'condition', False),
            FieldDef('spell_w3', 'Wizard Spells Lvl 3', 'W3', 'text', 'condition', False),
            FieldDef('spell_w4', 'Wizard Spells Lvl 4', 'W4', 'text', 'condition', False),
            FieldDef('spell_w5', 'Wizard Spells Lvl 5', 'W5', 'text', 'condition', False),
            FieldDef('spell_w6', 'Wizard Spells Lvl 6', 'W6', 'text', 'condition', False),
            FieldDef('spell_w7', 'Wizard Spells Lvl 7', 'W7', 'text', 'condition', False),
            FieldDef('spell_w8', 'Wizard Spells Lvl 8', 'W8', 'text', 'condition', False),
            FieldDef('spell_w9', 'Wizard Spells Lvl 9', 'W9', 'text', 'condition', False),
            FieldDef('spell_p1', 'Priest Spells Lvl 1', 'P1', 'text', 'condition', False),
            FieldDef('spell_p2', 'Priest Spells Lvl 2', 'P2', 'text', 'condition', False),
            FieldDef('spell_p3', 'Priest Spells Lvl 3', 'P3', 'text', 'condition', False),
            FieldDef('spell_p4', 'Priest Spells Lvl 4', 'P4', 'text', 'condition', False),
            FieldDef('spell_p5', 'Priest Spells Lvl 5', 'P5', 'text', 'condition', False),
            FieldDef('spell_p6', 'Priest Spells Lvl 6', 'P6', 'text', 'condition', False),
            FieldDef('spell_p7', 'Priest Spells Lvl 7', 'P7', 'text', 'condition', False),

            # ── Proficiencies ─────────────────────────────────────────────────
            # Weapon and non-weapon proficiencies stored as free text lists.
            FieldDef('weapon_profs',  'Weapon Proficiencies',     'WpnP', 'text', 'other', False),
            FieldDef('nwp',           'Non-Weapon Proficiencies', 'NWP',  'text', 'other', False),
            FieldDef('languages',     'Languages Known',          'Lang', 'text', 'other', False),
            FieldDef('special_abilities','Special Abilities',     'SpAb', 'text', 'other', False),
            FieldDef('notes',         'Notes',                    'Notes','text', 'other', False),
        ]

    def compute_derived(self, stats: dict) -> dict:
        """
        Derives ability adjustments per the 2e tables.
        Note: 2e modifiers are NOT (score-10)//2 — they use irregular lookup tables.
        We approximate with the standard formula for display purposes.
        The authoritative values should be entered manually per the PHB tables.
        """
        derived = {}

        def _mod(key):
            v = stats.get(key)
            if v is not None:
                try:
                    return (int(v) - 10) // 2
                except (ValueError, TypeError):
                    pass
            return None

        str_mod = _mod('strength')
        dex_mod = _mod('dexterity')
        con_mod = _mod('constitution')
        wis_mod = _mod('wisdom')

        for label, mod in [
            ('str_mod', str_mod), ('dex_mod', dex_mod),
            ('con_mod', con_mod), ('wis_mod', wis_mod),
        ]:
            if mod is not None:
                derived[label] = mod

        # Attack and damage adjustments from STR (if not already set)
        if 'attack_adj' not in stats and str_mod is not None:
            derived['attack_adj'] = str_mod
        if 'damage_adj' not in stats and str_mod is not None:
            derived['damage_adj'] = str_mod

        # Initiative adjustment from DEX (2e: lower is better, so negate)
        if 'initiative_adj' not in stats and dex_mod is not None:
            derived['initiative_adj'] = -dex_mod

        # Defensive AC bonus from DEX (subtract from AC since AC is descending)
        if dex_mod is not None:
            derived['dex_ac_adj'] = -dex_mod  # negative = better AC

        return derived
