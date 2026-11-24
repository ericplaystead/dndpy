# dndpy
A cli and web tabletop tool. 

I started an early version of this in 2016 that just sat for years. Using the main ideas and structure I had AI fix the many bugs and generally improve just about everything about it. 


Quick setup:

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally:

```bash
python dndpy.py
```
$ python dndpy.py

dndpy v0.9.0  tabletop character tracker
10 ruleset(s) loaded: adnd2e, coc, dnd35, dnd35sub, dnd5e, gammaworld4, generic, ma1e, pathfinder, pf2e


╭───────────────────────────────────╮
│  dndpy                            │
│  No character loaded  |  Generic  │
╰───────────────────────────────────╯
[1]   Open / Load character 
[2]   Show character card   
[3]   Companions & creatures
[4]   Items                 
[5]   Campaign management   
[6]   DM Tools              
[n]   New character         
[l]   Load ruleset          
[0]   Exit                  

> 


PROJECT GOALS:

Core concepts from inception, some of which have yet to be implimented.

1. Character tracking system for characters, familiars, items, full character stat block tracking and logic (similar perhaps to YAPCG) 

2. A game edition rules engine for loading 'module maps' to create character tracking for multiple game rules. 

3. Full suite of DM/GM and player tools for tabletop games, including;
	a. random item generator
	b. encounter generator 

4. A game engine for simulating character battles and interactions

5. Maintain open source licensing

6. Maintain working functionality for Linux and Windows


Alternatively you can run the following to launch the web server
```bash
python dndpy.py web
```
dndpy.py web currently only displays the database


