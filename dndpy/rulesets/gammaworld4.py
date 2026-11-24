"""
Gamma World 4th Edition ruleset (TSR, 1992).
Authors: Bruce Nesmith & James M. Ward.

Key differences from D&D-derived systems:
  - Seven ability scores with unique names: PS, DX, CN, MS, IN, CH, SN
  - Four genotypes: Pure Strain Human, Mutant Human, Mutant Animal, Mutant Plant
  - Four character classes: Enforcer, Esper, Examiner, Scout
  - Proto-d20 ascending AC system (AC 10–21), also Mental Defense (MD)
  - HP = roll CN d6; gain 3 + CN modifier per level
  - Three attack bonuses: THAC Melee (PS), THAC Ranged (DX), MHAC (MS)
  - Mutations stored as free-text lists (randomly rolled from tables in book)
  - Tech Level 0–IV for equipment/artifacts
  - Cryptic Alliance (optional faction membership)
  - No traditional saving throws — uses Health (10 + CN mod) vs. radiation/poison
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int, validate_choice
)

GENOTYPES = ['pure strain human', 'mutant human', 'mutant animal', 'mutant plant']

CLASSES = ['enforcer', 'esper', 'examiner', 'scout']

# Tech Levels 0–IV
TECH_LEVELS = ['0', 'I', 'II', 'III', 'IV']

CRYPTIC_ALLIANCES = [
    'brotherhood of thought', 'created', 'friends of entropy', 'healers',
    'knights of genetic purity', 'radioactivists', 'ranks of the fit',
    'restorationists', 'seekers', 'servants of the screen', 'traders',
    'zoopremacists', 'none',
]


def _ability_mod(score: int) -> int:
    """GW4e uses the same ability modifier formula as AD&D 2e."""
    return (score - 10) // 2


class GammaWorld4eRuleset(RulesetBase):
    RULESET_ID = 'gammaworld4'
    FULL_NAME = 'Gamma World 4th Edition'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'generic'

    def own_fields(self) -> list[FieldDef]:
        return [
            # ── Identity ─────────────────────────────────────────────────────
            FieldDef('name',          'Name',          'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',      'Campaign',      'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('genotype',      'Genotype',      'Type',  'text', 'identity', True,  validate_choice(GENOTYPES)),
            FieldDef('character_class','Class',         'Class', 'text', 'identity', True,  validate_choice(CLASSES)),
            FieldDef('level',         'Level',         'Lvl',   'int',  'identity', True,  validate_positive_int),
            FieldDef('experience',    'Experience',    'XP',    'int',  'identity', False, validate_nonneg_int, default=0),
            # Mutant Animals choose a base animal (e.g. "bear", "rat", etc.) — free text
            FieldDef('base_animal',   'Base Animal',   'Anml',  'text', 'identity', False),
            FieldDef('cryptic_alliance', 'Cryptic Alliance', 'Ally', 'text', 'identity', False,
                     validate_choice(CRYPTIC_ALLIANCES), default='none'),
            FieldDef('homeland',      'Homeland',      'Home',  'text', 'identity', False),

            # ── Ability Scores ────────────────────────────────────────────────
            # Seven GW4e primary attributes; all generated 3d6 during creation.
            FieldDef('physical_strength', 'Physical Strength', 'PS', 'int', 'ability', True, validate_int),
            FieldDef('dexterity',         'Dexterity',         'DX', 'int', 'ability', True, validate_int),
            FieldDef('constitution',      'Constitution',       'CN', 'int', 'ability', True, validate_int),
            FieldDef('mental_strength',   'Mental Strength',    'MS', 'int', 'ability', True, validate_int),
            FieldDef('intelligence',      'Intelligence',       'IN', 'int', 'ability', True, validate_int),
            FieldDef('charisma',          'Charisma',           'CH', 'int', 'ability', True, validate_int),
            FieldDef('senses',            'Senses',             'SN', 'int', 'ability', True, validate_int),

            # ── Combat ───────────────────────────────────────────────────────
            # HP = roll CN d6 at creation; gain 3 + CN-mod per level (min 3).
            FieldDef('hit_points',     'Hit Points',          'HP',    'int', 'combat', True,  validate_nonneg_int),
            FieldDef('hit_points_max', 'Max Hit Points',      'MaxHP', 'int', 'combat', True,  validate_positive_int),
            # AC: ascending, 10 + DX modifier (range 10–21 or beyond with gear)
            FieldDef('armor_class',    'Armor Class',         'AC',    'int', 'combat', False, validate_int, default=10),
            # MD: 10 + MS modifier — target for mental mutation attacks
            FieldDef('mental_defense', 'Mental Defense',      'MD',    'int', 'combat', False, validate_int, default=10),
            # Health: 10 + CN modifier — rolled against for poison, radiation, disease
            FieldDef('health',         'Health',              'Hlth',  'int', 'combat', False, validate_int, default=10),
            # Attack bonuses (modifiers; final to-hit = d20 + THAC vs target AC/MD)
            FieldDef('thac_melee',     'THAC Melee',          'THAC-M','int', 'combat', False, validate_int, default=0),
            FieldDef('thac_ranged',    'THAC Ranged',         'THAC-R','int', 'combat', False, validate_int, default=0),
            FieldDef('mhac',           'Mental THAC (MHAC)',  'MHAC',  'int', 'combat', False, validate_int, default=0),
            FieldDef('speed',          'Movement Speed (ft)', 'Spd',   'int', 'combat', False, validate_nonneg_int, default=30),
            FieldDef('initiative_mod', 'Initiative Modifier', 'Init',  'int', 'combat', False, validate_int, default=0),

            # ── Mutations ────────────────────────────────────────────────────
            # Mutations are rolled from random tables; stored as comma-separated
            # names. Power scores (4d6-L) are tracked separately per mutation
            # on the paper sheet — we capture the list and a notes block here.
            FieldDef('physical_mutations', 'Physical Mutations', 'PhysMut', 'text', 'other', False),
            FieldDef('mental_mutations',   'Mental Mutations',   'MntlMut', 'text', 'other', False),
            FieldDef('plant_mutations',    'Plant Mutations',    'PlntMut', 'text', 'other', False),
            FieldDef('mutation_defects',   'Defects',            'Defects', 'text', 'other', False),
            FieldDef('mutation_notes',     'Mutation Notes',     'MutNote', 'text', 'other', False),

            # ── Skills ───────────────────────────────────────────────────────
            # General skills (all characters); class skills listed in notes.
            # GW4e resolves skills as: d20 + difficulty modifier vs. base score.
            FieldDef('skill_perception',   'Perception',      'Percep', 'int', 'skills', False, validate_int),
            FieldDef('skill_stealth',      'Stealth',         'Stlth',  'int', 'skills', False, validate_int),
            FieldDef('skill_use_artifact', 'Use Artifacts',   'UseArt', 'int', 'skills', False, validate_int),
            FieldDef('skill_robot_recog',  'Robot Recognition','RobRec','int', 'skills', False, validate_int),
            # Class-specific skills — free text since they vary entirely by class
            FieldDef('class_skills',       'Class Skills',    'ClsSk',  'text', 'other',  False),

            # ── Equipment / Tech ─────────────────────────────────────────────
            FieldDef('tech_level', 'Tech Level', 'TL', 'text', 'other', False,
                     validate_choice(TECH_LEVELS), default='I'),
            FieldDef('credits',    'Credits',    'Cr', 'int',  'other', False, validate_nonneg_int, default=0),
            FieldDef('notes',      'Notes',      'Notes', 'text', 'other', False),
        ]

    def compute_derived(self, stats: dict) -> dict:
        """
        Derives ability modifiers and the three standard defense/attack values
        if the base ability scores are present. These are shown on the card but
        not stored in the DB — the raw ability scores are the source of truth.
        """
        derived = {}

        def _mod(key):
            v = stats.get(key)
            if v is not None:
                try:
                    return _ability_mod(int(v))
                except (ValueError, TypeError):
                    pass
            return None

        ps_mod = _mod('physical_strength')
        dx_mod = _mod('dexterity')
        cn_mod = _mod('constitution')
        ms_mod = _mod('mental_strength')
        in_mod = _mod('intelligence')
        ch_mod = _mod('charisma')
        sn_mod = _mod('senses')

        for key, mod in [
            ('ps_mod', ps_mod), ('dx_mod', dx_mod), ('cn_mod', cn_mod),
            ('ms_mod', ms_mod), ('in_mod', in_mod), ('ch_mod', ch_mod),
            ('sn_mod', sn_mod),
        ]:
            if mod is not None:
                derived[key] = mod

        # AC = 10 + DX mod (if not manually overridden and base score exists)
        if 'armor_class' not in stats and dx_mod is not None:
            derived['armor_class'] = 10 + dx_mod

        # MD = 10 + MS mod
        if 'mental_defense' not in stats and ms_mod is not None:
            derived['mental_defense'] = 10 + ms_mod

        # Health = 10 + CN mod
        if 'health' not in stats and cn_mod is not None:
            derived['health'] = 10 + cn_mod

        # THAC defaults from ability mods
        if 'thac_melee' not in stats and ps_mod is not None:
            derived['thac_melee'] = ps_mod
        if 'thac_ranged' not in stats and dx_mod is not None:
            derived['thac_ranged'] = dx_mod
        if 'mhac' not in stats and ms_mod is not None:
            derived['mhac'] = ms_mod

        # Perception = SN score + IN mod
        sn = stats.get('senses')
        if sn is not None and in_mod is not None:
            try:
                derived['skill_perception_derived'] = int(sn) + in_mod
            except (ValueError, TypeError):
                pass

        return derived
