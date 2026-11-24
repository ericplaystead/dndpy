# Custom Rulesets

Drop `.py` files in this directory to add your own game system rulesets.

## Minimal example

```python
from dndpy.rulesets.base import RulesetBase, FieldDef
from dndpy.utils.validators import validate_nonempty, validate_int

class MyGameRuleset(RulesetBase):
    RULESET_ID = 'mygame'           # unique slug, no spaces
    FULL_NAME = 'My Game System'
    VERSION = '1.0'
    CARD_LAYOUT = 'generic'         # 'dnd', 'coc', or 'generic'

    def own_fields(self):
        return [
            FieldDef('name',   'Name',   'Name', 'text', 'identity', True,  validate_nonempty),
            FieldDef('health', 'Health', 'HP',   'int',  'condition', True, validate_int),
            # Add as many fields as your game needs
        ]
```

## Field sections
- `identity`  — name, class, campaign, race, background info
- `ability`   — core stat scores
- `combat`    — HP, AC, attack bonuses
- `saves`     — saving throws
- `condition` — current status (XP, spell slots, sanity)
- `skills`    — skill ranks/bonuses
- `other`     — anything else

## Inheriting from an existing ruleset
```python
from dndpy.rulesets.dnd35 import DnD35Ruleset

class MyVariantRuleset(DnD35Ruleset):
    RULESET_ID = 'myvariant'
    FULL_NAME = 'My D&D Variant'

    def own_fields(self):
        parent = super().own_fields()
        my_extras = [
            FieldDef('sanity', 'Sanity', 'SAN', 'int', 'condition', False, validate_int),
        ]
        return parent + my_extras
```
