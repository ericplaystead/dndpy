#!/usr/bin/env python3
"""
dndpy — tabletop RPG character tracker
Entry point. Run with: python dndpy.py
"""
import os
import sys

# Ensure the project root is on the path regardless of where we're invoked from
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from dndpy.cli.app import cli

if __name__ == '__main__':
    cli()
