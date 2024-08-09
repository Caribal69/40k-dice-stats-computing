"""
Here are the usefull data to launch the workflow.

By default, the script test_workflow.py works if the params in this utils.py are all set to False.
"""
from os.path import dirname, abspath, join
import pandas as pd

# ENV PATH
SRC_PATH = dirname(abspath(__file__))
# <absolute_path>/android/src/
ROOT_PATH = dirname(SRC_PATH)
# <absolute_path>/android/

nb_figs=10
# If True, print lots of things (default False). Set to True for debug.
VERBOSE = True

# If True, re-roll all dices which not proc critical (to maximize devastating wound)
# NB: if True: twin set to False.
# re_roll_non_devastating_wound=True

# Set the value of the critical (5 mean 5+, default 6+)
crit=6

# Weapon
# ---------------------------
# Number of attack of the weapon
weapon_a="D3+1"
# Set the hit capacity
hit_threshold=3
# Strenght of the weapon
weapon_s=4
# PA (3 means -3, 0 means no PA)
weapon_ap=1
# Damage of the weapon
weapon_d=2

# Bonus
# ---------------------------
# No bonus on hit threshold

# Bonus wound (1 means +1 to wound, 0 means no bonus, -1 means malus of -1 to wound)
bonus_wound=0
# If True, do not launch any hit dice
torrent=False
# If True, reroll the one during the hit launch.
rr_hit_ones=False
# If True, re-roll all failed hit
rr_hit_all=False
# Set the sustain hit of the weapon (0 means no sustain hit)
# Can be a str (ex: D3)
sustain_hit="D3"
# lethal hit: if True: enable lethal hit
lethal_hit=False
# If True, re-roll the one during wound launch.
rr_wounds_ones=False
# If True, reroll all failed wounds
twin=False
# If True: enable devastating wounds (critical wounds raises
devastating_wounds=False

# Ennemy
# ---------------------------
# Endurance of the enemy
enemy_toughness=4
# Svg enemy (4 means 4+, 7 means no save)
svg_enemy=3
# Invulnerable save of the enemy (4 means 4+, 7 means no save)
svg_invul_enemy=6
# Feel no Pain (FNP) (4 means 4+, 7 means no FNP), default 7
fnp_enemy=5
# HP of the ennemy
ennemy_hp = 3

# Datasheets of typical ennemy (marine, monster, tank, ...)
# ------------------------------------------
# Path to the CSV to read
OPPONENT_DATA_PATH = join(ROOT_PATH, "data", "enemy.csv")

# Get access to the opponent list
opponent_datasheets = pd.read_csv(OPPONENT_DATA_PATH, sep=";")

# Fill the cells not filled by user (e.g. feel no pain): filled with 7 (e.g. no feel no pain)
opponent_datasheets = opponent_datasheets.fillna(7)
# Example:
#                     Name  svg  svg invul  feel no pain  toughness   w
# 0                 marine    3        7           7          4   2


