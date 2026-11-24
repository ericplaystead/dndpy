"""Campaign management: create, list, switch."""
from rich.console import Console
from rich.table import Table
from dndpy.cli.menus import BACK
from dndpy.cli import prompts
from dndpy.db import repository as repo

console = Console()


def campaign_menu(session: dict):
    from dndpy.cli.menus import Menu, MenuItem
    menu = Menu('Campaign Management', [
        MenuItem('1', 'Create campaign',  create_campaign),
        MenuItem('2', 'Switch campaign',  switch_campaign),
        MenuItem('3', 'List campaigns',   list_campaigns),
        MenuItem('0', 'Back',             lambda s: BACK),
    ], session)
    menu.run()


def create_campaign(session: dict):
    ruleset = session.get('ruleset')
    db = session['db']
    if not ruleset:
        prompts.warn('Load a ruleset first.')
        return

    name = prompts.ask('Campaign name', validator=lambda s: (s.strip(), None if s.strip() else 'Required'))
    desc = prompts.ask('Description (optional)', default='')

    existing = repo.get_campaign(db, name)
    if existing:
        prompts.warn(f"Campaign '{name}' already exists.")
        return

    campaign = repo.create_campaign(db, name=name, ruleset_id=ruleset.RULESET_ID, description=desc)
    session['campaign_id'] = campaign.id
    prompts.info(f"✓ Campaign '{name}' created and active.")


def switch_campaign(session: dict):
    db = session['db']
    campaigns = repo.list_campaigns(db)
    if not campaigns:
        prompts.warn('No campaigns yet. Create one first.')
        return

    chosen = prompts.ask_choice(
        'Select campaign',
        choices=campaigns,
        display=[f'{c.name}  [dim]({c.ruleset_id})[/]' for c in campaigns],
    )
    session['campaign_id'] = chosen.id
    # Switch ruleset to match campaign's ruleset
    rulesets = session.get('rulesets', {})
    if chosen.ruleset_id in rulesets:
        session['ruleset'] = rulesets[chosen.ruleset_id]
    prompts.info(f"Switched to campaign: {chosen.name}")


def list_campaigns(session: dict):
    db = session['db']
    campaigns = repo.list_campaigns(db)
    if not campaigns:
        prompts.warn('No campaigns found.')
        return

    table = Table(title='Campaigns', show_header=True, header_style='bold blue')
    table.add_column('Name')
    table.add_column('Ruleset')
    table.add_column('Description')
    for c in campaigns:
        table.add_row(c.name, c.ruleset_id, c.description or '')
    console.print(table)
