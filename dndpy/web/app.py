"""
dndpy Flask web application.
Currently: single admin route showing full DB state.
"""
import os
import flask
from dndpy.db.engine import init_db, get_session
from dndpy.db.models import Campaign, Character, CharacterStat, Item, RulesetRegistry

_HERE = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__, template_folder=os.path.join(_HERE, 'templates'))
_engine = None


def _get_db():
    if 'db' not in flask.g:
        flask.g.db = get_session(_engine)
    return flask.g.db


@app.teardown_appcontext
def close_db(exc):
    db = flask.g.pop('db', None)
    if db:
        db.close()


@app.route('/')
def admin():
    db = _get_db()

    campaigns = db.query(Campaign).order_by(Campaign.name).all()
    characters = db.query(Character).order_by(Character.name).all()
    items = db.query(Item).order_by(Item.name).all()
    rulesets = db.query(RulesetRegistry).order_by(RulesetRegistry.ruleset_id).all()

    data = {
        'rulesets': [
            {'id': r.ruleset_id, 'name': r.full_name, 'version': r.version}
            for r in rulesets
        ],
        'campaigns': [
            {
                'id': c.id,
                'name': c.name,
                'ruleset_id': c.ruleset_id,
                'description': c.description,
                'created_at': c.created_at.isoformat() if c.created_at else None,
            }
            for c in campaigns
        ],
        'characters': [
            {
                'id': ch.id,
                'name': ch.name,
                'ruleset_id': ch.ruleset_id,
                'character_type': ch.character_type,
                'campaign': ch.campaign.name if ch.campaign else None,
                'owner': ch.owner.name if ch.owner else None,
                'stats': {
                    s.stat_key: s.stat_value_int if s.stat_type == 'int' else s.stat_value_text
                    for s in ch.stats
                },
                'items': [
                    {'name': i.name, 'quantity': i.quantity, 'weight': i.weight}
                    for i in ch.items
                ],
            }
            for ch in characters
        ],
    }

    return flask.render_template('admin.html', data=data)


def create_app(db_path=None):
    global _engine
    _engine = init_db(db_path=db_path) if db_path else init_db()
    return app
