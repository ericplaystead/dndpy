"""
Character create / load / edit / unload / show card.
"""
from rich.console import Console
from dndpy.cli.menus import Menu, MenuItem, BACK, EXIT
from dndpy.cli import prompts
from dndpy.db import repository as repo
from dndpy.card import renderer

console = Console()


def _require_character(session: dict) -> bool:
    return session.get('character') is not None


def _require_no_character(session: dict) -> bool:
    return session.get('character') is None


def create_character(session: dict):
    ruleset = session.get('ruleset')
    db = session['db']

    if not ruleset:
        prompts.warn('Load a ruleset first (option L).')
        return

    prompts.info(f'\nCreating new character [{ruleset.FULL_NAME}]')
    prompts.info('Fill in the required fields. Press Enter to skip optional ones.\n')

    char_data = {}
    for fd in ruleset.creation_fields():
        raw = prompts.ask(fd.label, default=str(fd.default) if fd.default is not None else None,
                          validator=fd.validator)
        char_data[fd.key] = raw

    name = char_data.get('name', '').strip()
    if not name:
        prompts.error('Name is required.')
        return

    # Check if character already exists in this ruleset
    existing = repo.get_character(db, name, ruleset_id=ruleset.RULESET_ID,
                                  campaign_id=session.get('campaign_id'))
    if existing:
        prompts.warn(f"Character '{name}' already exists in this ruleset.")
        if not prompts.confirm('Overwrite?'):
            return
        char = existing
    else:
        campaign_id = session.get('campaign_id')
        char = repo.create_character(
            db, name=name, ruleset_id=ruleset.RULESET_ID,
            campaign_id=campaign_id, character_type='pc'
        )

    # Write all creation stats
    for fd in ruleset.creation_fields():
        if fd.key == 'name':
            continue
        val = char_data.get(fd.key)
        if val is not None and val != '':
            char.set_stat(fd.key, val, fd.stat_type)
    db.commit()

    session['character'] = char
    prompts.info(f"\n✓ Character '{name}' created and loaded.")
    renderer.print_card(char, ruleset, db)


def load_character(session: dict):
    ruleset = session.get('ruleset')
    db = session['db']

    if not ruleset:
        prompts.warn('Load a ruleset first (option L).')
        return

    characters = repo.list_characters(db, ruleset_id=ruleset.RULESET_ID,
                                      campaign_id=session.get('campaign_id'))
    if not characters:
        prompts.warn('No characters found. Create one first (option N).')
        return

    char = prompts.ask_choice(
        'Select character',
        choices=characters,
        display=[f'{c.name}  [dim](campaign: {c.campaign.name if c.campaign else "—"})[/]'
                 for c in characters],
    )
    session['character'] = char
    prompts.info(f"Loaded: {char.name}")


def unload_character(session: dict):
    char = session.get('character')
    if char:
        prompts.info(f'Unloaded {char.name}.')
        session['character'] = None
    return BACK


def show_card(session: dict):
    char = session.get('character')
    ruleset = session.get('ruleset')
    db = session['db']
    if not char:
        prompts.warn('No character loaded.')
        return
    renderer.print_card(char, ruleset, db)


def edit_character(session: dict):
    char = session.get('character')
    ruleset = session.get('ruleset')
    db = session['db']

    if not char:
        prompts.warn('No character loaded.')
        return

    # Build edit menu grouped by section
    sections = ruleset.field_sections()
    items = []
    all_fields_list = ruleset.all_fields()
    key_counter = 1

    # Assign numeric keys to editable fields
    field_keys = {}
    for section_name, fields in sections.items():
        for fd in fields:
            if fd.editable:
                k = str(key_counter)
                current = char.get_stat(fd.key)
                current_str = f' [dim]({current})[/]' if current is not None else ''
                label = f'[{section_name.upper()}] {fd.label}{current_str}'

                def _make_handler(field_def, character, session):
                    def handler(s):
                        _edit_field(s, character, field_def, s['db'])
                    return handler

                items.append(MenuItem(k, label, _make_handler(fd, char, session)))
                field_keys[k] = fd
                key_counter += 1

    items.append(MenuItem('0', 'Back', lambda s: BACK))

    menu = Menu(f'Edit: {char.name}', items, session)
    menu.run()


def _edit_field(session: dict, char, field_def, db):
    current = char.get_stat(field_def.key)
    new_val = prompts.ask(
        f'{field_def.label}',
        default=str(current) if current is not None else None,
        validator=field_def.validator,
    )
    if new_val is not None and new_val != '':
        char.set_stat(field_def.key, new_val, field_def.stat_type)
        db.commit()
        prompts.info(f'  ✓ {field_def.label} updated.')
