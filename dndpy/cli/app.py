"""
Main CLI application.
Sets up the session, discovers rulesets, runs the interactive menu.
"""
import logging
import os
import click
from rich.console import Console

from dndpy.db.engine import init_db, get_session
from dndpy.db import repository as repo
from dndpy.rulesets import discover_rulesets
from dndpy.cli.menus import Menu, MenuItem, EXIT, BACK
from dndpy.cli import prompts
from dndpy.cli.commands import character, campaign, companions, items, dm_tools

console = Console()
log = logging.getLogger('dndpy')

VERSION = '0.9.0'


def _has_character(session):
    return session.get('character') is not None


def _no_character(session):
    return session.get('character') is None


def _load_ruleset(session):
    rulesets = session['rulesets']
    if not rulesets:
        prompts.warn('No rulesets found.')
        return

    choices = list(rulesets.values())
    chosen = prompts.ask_choice(
        'Select ruleset',
        choices=choices,
        display=[f'{rs.FULL_NAME} [dim]({rs.RULESET_ID})[/]' for rs in choices],
    )
    session['ruleset'] = chosen
    prompts.info(f'Ruleset loaded: {chosen.FULL_NAME}')


def _unload_character(session):
    char = session.get('character')
    if char:
        prompts.info(f'Unloaded {char.name}.')
        session['character'] = None


def build_main_menu(session) -> Menu:
    char_label = lambda: (
        f'Open/Load character'
        if not session.get('character')
        else f'Edit character  [dim]({session["character"].name})[/]'
    )

    items_list = [
        MenuItem('1', 'Open / Load character',     character.load_character,
                 condition=_no_character),
        MenuItem('1', 'Edit character',            character.edit_character,
                 condition=_has_character),
        MenuItem('2', 'Show character card',       character.show_card),
        MenuItem('3', 'Companions & creatures',    companions.companions_menu),
        MenuItem('4', 'Items',                     items.items_menu),
        MenuItem('5', 'Campaign management',       campaign.campaign_menu),
        MenuItem('6', 'DM Tools',                  dm_tools.dm_tools_menu),
        MenuItem('n', 'New character',             character.create_character),
        MenuItem('l', 'Load ruleset',              _load_ruleset),
        MenuItem('u', 'Unload character',          lambda s: _unload_character(s),
                 condition=_has_character),
        MenuItem('0', 'Exit',                      lambda s: EXIT),
    ]

    return Menu('dndpy', items_list, session)


@click.group(invoke_without_command=True)
@click.version_option(VERSION, prog_name='dndpy')
@click.option('--db', default=None, help='Path to database file')
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.pass_context
def cli(ctx, db, verbose):
    """dndpy — tabletop RPG character tracker"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if ctx.invoked_subcommand is None:
        ctx.invoke(play, db=db)


@cli.command()
@click.option('--db', default=None, help='Path to database file')
def play(db):
    """Start the interactive session."""
    engine = init_db(db_path=db) if db else init_db()
    db_session = get_session(engine)

    rulesets = discover_rulesets()
    repo.sync_ruleset_registry(db_session, rulesets)

    session = {
        'db': db_session,
        'rulesets': rulesets,
        'ruleset': rulesets.get('generic'),
        'character': None,
        'campaign_id': None,
    }

    console.print(f'\n[bold blue]dndpy v{VERSION}[/]  [dim]tabletop character tracker[/]')
    console.print(f'[dim]{len(rulesets)} ruleset(s) loaded: {", ".join(rulesets.keys())}[/]\n')

    menu = build_main_menu(session)
    menu.run()

    db_session.close()
    console.print('\n[dim]Goodbye.[/]')


@cli.command()
@click.option('--db', default=None, help='Path to database file')
@click.option('--host', default='127.0.0.1', show_default=True)
@click.option('--port', default=5000, show_default=True)
@click.option('--debug', is_flag=True, default=False)
def web(db, host, port, debug):
    """Start the Flask web admin server."""
    from dndpy.web.app import create_app
    flask_app = create_app(db_path=db)
    console.print(f'[bold blue]dndpy web[/]  [dim]http://{host}:{port}/[/]')
    flask_app.run(host=host, port=port, debug=debug)
