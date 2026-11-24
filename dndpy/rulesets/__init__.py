"""
Ruleset plugin loader.
Discovers built-in rulesets and user_rulesets/ drop-ins.
"""
import importlib.util
import inspect
import logging
import os

from dndpy.rulesets.base import RulesetBase

logger = logging.getLogger('dndpy.rulesets')

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BUILTIN_DIR = os.path.dirname(os.path.abspath(__file__))
_USER_DIR = os.path.join(_PROJECT_ROOT, 'user_rulesets')

_SKIP = {'base', '__init__'}


def _load_from_file(path: str, module_name: str) -> list:
    instances = []
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for _name, obj in inspect.getmembers(mod, inspect.isclass):
            if (issubclass(obj, RulesetBase)
                    and obj is not RulesetBase
                    and obj.__module__ == module_name):
                rs = obj()
                if rs.RULESET_ID and rs.FULL_NAME:
                    instances.append(rs)
                else:
                    logger.warning('Skipping %s: missing RULESET_ID or FULL_NAME', _name)
    except Exception as e:
        logger.warning('Failed to load ruleset from %s: %s', path, e)
    return instances


def discover_rulesets() -> dict:
    """
    Scan built-in and user ruleset directories.
    Returns dict keyed by RULESET_ID.
    User rulesets override built-ins with the same ID.
    """
    rulesets = {}

    for directory, prefix in [(_BUILTIN_DIR, 'dndpy.rulesets'), (_USER_DIR, 'user_rulesets')]:
        if not os.path.isdir(directory):
            continue
        for fname in sorted(os.listdir(directory)):
            if not fname.endswith('.py'):
                continue
            stem = fname[:-3]
            if stem in _SKIP:
                continue
            path = os.path.join(directory, fname)
            module_name = f'{prefix}.{stem}'
            for rs in _load_from_file(path, module_name):
                if rs.RULESET_ID in rulesets:
                    logger.info('User ruleset %r overrides built-in', rs.RULESET_ID)
                rulesets[rs.RULESET_ID] = rs
                logger.debug('Loaded ruleset: %s (%s)', rs.RULESET_ID, rs.FULL_NAME)

    return rulesets
