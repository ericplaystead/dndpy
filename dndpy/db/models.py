from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from dndpy.db.engine import Base


class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    ruleset_id = Column(String, nullable=False)
    description = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)

    characters = relationship('Character', back_populates='campaign',
                              foreign_keys='Character.campaign_id')

    def __repr__(self):
        return f'<Campaign {self.name!r} ruleset={self.ruleset_id!r}>'


CHARACTER_TYPES = ('pc', 'npc', 'familiar', 'mount', 'companion', 'summoned')


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ruleset_id = Column(String, nullable=False)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=True)
    character_type = Column(
        Enum(*CHARACTER_TYPES, name='character_type'),
        nullable=False,
        default='pc'
    )
    owner_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship('Campaign', back_populates='characters',
                            foreign_keys=[campaign_id])
    stats = relationship('CharacterStat', back_populates='character',
                         cascade='all, delete-orphan')
    items = relationship('Item', back_populates='character',
                         cascade='all, delete-orphan')
    # companions, familiars, mounts, summoned — all are characters with owner_id
    owned_creatures = relationship(
        'Character',
        foreign_keys=[owner_id],
        primaryjoin='Character.owner_id == Character.id',
        back_populates='owner',
    )
    owner = relationship(
        'Character',
        foreign_keys=[owner_id],
        primaryjoin='Character.owner_id == Character.id',
        back_populates='owned_creatures',
        remote_side='Character.id',
    )

    def get_stat(self, key: str):
        for s in self.stats:
            if s.stat_key == key:
                return s.stat_value_int if s.stat_type == 'int' else s.stat_value_text
        return None

    def set_stat(self, key: str, value, stat_type: str = 'int'):
        for s in self.stats:
            if s.stat_key == key:
                if stat_type == 'int':
                    s.stat_value_int = int(value) if value not in (None, '') else None
                else:
                    s.stat_value_text = str(value) if value is not None else None
                s.stat_type = stat_type
                return
        stat = CharacterStat(
            character=self,
            stat_key=key,
            stat_type=stat_type,
        )
        if stat_type == 'int':
            stat.stat_value_int = int(value) if value not in (None, '') else None
        else:
            stat.stat_value_text = str(value) if value is not None else None
        self.stats.append(stat)

    def as_dict(self) -> dict:
        d = {
            'id': self.id,
            'name': self.name,
            'ruleset_id': self.ruleset_id,
            'character_type': self.character_type,
            'campaign': self.campaign.name if self.campaign else None,
        }
        for s in self.stats:
            d[s.stat_key] = s.stat_value_int if s.stat_type == 'int' else s.stat_value_text
        return d

    def __repr__(self):
        return f'<Character {self.name!r} type={self.character_type!r} ruleset={self.ruleset_id!r}>'


class CharacterStat(Base):
    __tablename__ = 'character_stats'
    __table_args__ = (UniqueConstraint('character_id', 'stat_key'),)

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    stat_key = Column(String, nullable=False)
    stat_value_text = Column(Text, nullable=True)
    stat_value_int = Column(Integer, nullable=True)
    stat_type = Column(String, nullable=False, default='int')

    character = relationship('Character', back_populates='stats')


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    quantity = Column(Integer, default=1)
    weight = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    character = relationship('Character', back_populates='items')

    def __repr__(self):
        return f'<Item {self.name!r} qty={self.quantity}>'


class RulesetRegistry(Base):
    __tablename__ = 'ruleset_registry'

    id = Column(Integer, primary_key=True)
    ruleset_id = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    version = Column(String, default='1.0')
