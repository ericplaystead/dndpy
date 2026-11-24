"""
Metamorphosis Alpha 1st Edition (TSR, 1976).
Designer: James M. Ward.

The first science-fiction RPG. Characters are survivors — and their
descendants — aboard the generation ship Warden, which suffered a
catastrophic radiation accident centuries ago. Most of the crew died;
those who survived mutated. The ship's AI and robots still function,
but no one fully understands the technology anymore.

Key differences from D&D-derived systems:
  - Four character types: Pure Strain Human, Mutant Human, Mutant Animal,
    Mutant Plant. Type shapes mutation access and available stats.
  - Four core ability scores: Strength, Dexterity, Constitution,
    Mental Resistance. PSH characters also have Leadership Potential.
  - Radiation Resistance rating (3d6, 3–18): like a CON check vs. radiation.
  - Descending AC (9 unarmored, lower is better — inherited from OD&D).
  - No alignment system; no saving throw categories.
  - Mutations rolled randomly from tables: physical and mental variants.
    Defect mutations also possible. Stored as free-text lists.
  - Tech items rated by Complexity Class (I–VI). Use requires a roll vs. INT.
  - Currency: credits. No coinage; all barter or salvaged tech.
  - Location tracked as Warden deck/section (ship has 17 decks, hundreds of areas).
"""
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import (
    validate_nonempty, validate_int, validate_nonneg_int,
    validate_positive_int, validate_choice
)

CHARACTER_TYPES = [
    'pure strain human',
    'mutant human',
    'mutant animal',
    'mutant plant',
]

# Complexity Classes for tech artifacts (I = simple tools, VI = advanced AI systems)
COMPLEXITY_CLASSES = ['I', 'II', 'III', 'IV', 'V', 'VI']


def _rad_resistance_mod(rr: int) -> int:
    """Modifier applied to saves vs. radiation. Linear with the score."""
    return (rr - 9)


class MetamorphosisAlpha1eRuleset(RulesetBase):
    RULESET_ID = 'ma1e'
    FULL_NAME = 'Metamorphosis Alpha 1e'
    VERSION = '1.0'
    PARENT_RULESET_ID = None
    CARD_LAYOUT = 'generic'

    def own_fields(self) -> list[FieldDef]:
        return [
            # ── Identity ─────────────────────────────────────────────────────
            FieldDef('name',           'Name',           'Name',  'text', 'identity', True,  validate_nonempty),
            FieldDef('campaign',       'Campaign',       'Camp',  'text', 'identity', False, validate_nonempty),
            FieldDef('character_type', 'Character Type', 'Type',  'text', 'identity', True,
                     validate_choice(CHARACTER_TYPES)),
            # Mutant Animals choose a base animal (e.g. "wolf", "rat") — free text
            FieldDef('base_animal',    'Base Animal',    'Anml',  'text', 'identity', False),
            # Warden location: deck number and area name, e.g. "Deck 7 / Cargo Bay 3"
            FieldDef('warden_location','Warden Location','Loc',   'text', 'identity', False),

            # ── Ability Scores ────────────────────────────────────────────────
            # All characters: STR, DEX, CON, MR (3d6 each)
            FieldDef('strength',         'Strength',         'STR', 'int', 'ability', True, validate_int),
            FieldDef('dexterity',        'Dexterity',        'DEX', 'int', 'ability', True, validate_int),
            FieldDef('constitution',     'Constitution',     'CON', 'int', 'ability', True, validate_int),
            # Mental Resistance: defense vs. mental mutations and psionic attack
            FieldDef('mental_resistance','Mental Resistance','MR',  'int', 'ability', True, validate_int),
            # Leadership Potential: Pure Strain Humans only (3d6).
            # Governs how many mutants/robots will follow and obey them.
            FieldDef('leadership_potential','Leadership Potential','LP','int','ability',False, validate_int),

            # ── Combat ───────────────────────────────────────────────────────
            FieldDef('hit_points',      'Hit Points',       'HP',    'int', 'combat', True,  validate_nonneg_int),
            FieldDef('hit_points_max',  'Max Hit Points',   'MaxHP', 'int', 'combat', True,  validate_positive_int),
            # Descending AC: 9 unarmored; lower is better (like OD&D).
            FieldDef('armor_class',     'Armor Class',      'AC',    'int', 'combat', False, validate_int, default=9),
            # Radiation Resistance: 3d6 roll at creation (3–18). Higher is better.
            # Used as the threshold when rolling to resist radiation damage.
            FieldDef('radiation_resistance','Radiation Resistance','RR','int','combat',True,validate_int),

            # ── Mutations ────────────────────────────────────────────────────
            # Rolled from tables during character creation; recorded as free text.
            FieldDef('physical_mutations','Physical Mutations','PhyMut','text','other',False),
            FieldDef('mental_mutations',  'Mental Mutations', 'MntMut','text','other',False),
            FieldDef('defect_mutations',  'Defect Mutations', 'Defect','text','other',False),

            # ── Equipment / Tech ─────────────────────────────────────────────
            # Complexity Class of highest artifact the character can reliably operate
            FieldDef('max_complexity',  'Max Artifact CC',  'MaxCC', 'text', 'other', False,
                     validate_choice(COMPLEXITY_CLASSES), default='I'),
            FieldDef('credits',         'Credits',          'Cr',    'int',  'other', False, validate_nonneg_int, default=0),
            FieldDef('equipment',       'Equipment',        'Equip', 'text', 'other', False),
            FieldDef('notes',           'Notes',            'Notes', 'text', 'other', False),
        ]

    def compute_derived(self, stats: dict) -> dict:
        derived = {}

        for key, short in [
            ('strength', 'str'), ('dexterity', 'dex'), ('constitution', 'con'),
            ('mental_resistance', 'mr'),
        ]:
            score = stats.get(key)
            if score is not None:
                try:
                    derived[f'{short}_mod'] = (int(score) - 10) // 2
                except (ValueError, TypeError):
                    pass

        # Radiation resistance modifier for display
        rr = stats.get('radiation_resistance')
        if rr is not None:
            try:
                derived['rr_mod'] = _rad_resistance_mod(int(rr))
            except (ValueError, TypeError):
                pass

        return derived
