"""
All database operations go through this module.
No raw SQL or ORM queries outside of here — keeps the web layer simple to add later.
"""
from typing import Optional
from sqlalchemy.orm import Session
from dndpy.db.models import Campaign, Character, CharacterStat, Item, RulesetRegistry


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

def create_campaign(session: Session, name: str, ruleset_id: str,
                    description: str = '') -> Campaign:
    campaign = Campaign(name=name, ruleset_id=ruleset_id, description=description)
    session.add(campaign)
    session.commit()
    return campaign


def get_campaign(session: Session, name: str) -> Optional[Campaign]:
    return session.query(Campaign).filter_by(name=name).first()


def get_campaign_by_id(session: Session, campaign_id: int) -> Optional[Campaign]:
    return session.get(Campaign, campaign_id)


def list_campaigns(session: Session) -> list[Campaign]:
    return session.query(Campaign).order_by(Campaign.name).all()


# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------

def create_character(session: Session, name: str, ruleset_id: str,
                     campaign_id: Optional[int] = None,
                     character_type: str = 'pc',
                     owner_id: Optional[int] = None) -> Character:
    char = Character(
        name=name,
        ruleset_id=ruleset_id,
        campaign_id=campaign_id,
        character_type=character_type,
        owner_id=owner_id,
    )
    session.add(char)
    session.commit()
    return char


def get_character(session: Session, name: str,
                  ruleset_id: Optional[str] = None,
                  campaign_id: Optional[int] = None) -> Optional[Character]:
    q = session.query(Character).filter_by(name=name, character_type='pc')
    if ruleset_id:
        q = q.filter_by(ruleset_id=ruleset_id)
    if campaign_id:
        q = q.filter_by(campaign_id=campaign_id)
    return q.first()


def get_character_by_id(session: Session, char_id: int) -> Optional[Character]:
    return session.get(Character, char_id)


def list_characters(session: Session, ruleset_id: Optional[str] = None,
                    campaign_id: Optional[int] = None,
                    character_type: str = 'pc') -> list[Character]:
    q = session.query(Character).filter_by(character_type=character_type)
    if ruleset_id:
        q = q.filter_by(ruleset_id=ruleset_id)
    if campaign_id:
        q = q.filter_by(campaign_id=campaign_id)
    return q.order_by(Character.name).all()


def list_owned_creatures(session: Session, owner_id: int) -> list[Character]:
    return (session.query(Character)
            .filter(Character.owner_id == owner_id)
            .order_by(Character.character_type, Character.name)
            .all())


def set_stat(session: Session, character: Character,
             key: str, value, stat_type: str = 'int'):
    character.set_stat(key, value, stat_type)
    session.commit()


def delete_character(session: Session, character: Character):
    session.delete(character)
    session.commit()


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

def add_item(session: Session, character: Character, name: str,
             quantity: int = 1, weight: str = '', notes: str = '') -> Item:
    item = Item(name=name, character=character,
                quantity=quantity, weight=weight, notes=notes)
    session.add(item)
    session.commit()
    return item


def list_items(session: Session, character: Character) -> list[Item]:
    return (session.query(Item)
            .filter_by(character_id=character.id)
            .order_by(Item.name)
            .all())


def remove_item(session: Session, item: Item):
    session.delete(item)
    session.commit()


def get_item_by_id(session: Session, item_id: int) -> Optional[Item]:
    return session.get(Item, item_id)


# ---------------------------------------------------------------------------
# Ruleset registry
# ---------------------------------------------------------------------------

def sync_ruleset_registry(session: Session, rulesets: dict):
    """Upsert all discovered rulesets into the registry table."""
    for ruleset_id, rs in rulesets.items():
        existing = session.query(RulesetRegistry).filter_by(ruleset_id=ruleset_id).first()
        if existing:
            existing.full_name = rs.FULL_NAME
            existing.version = rs.VERSION
        else:
            session.add(RulesetRegistry(
                ruleset_id=ruleset_id,
                full_name=rs.FULL_NAME,
                version=rs.VERSION,
            ))
    session.commit()
