"""
Global workflow to launch.

Note on specificity:
    * When AP is applied, check if the invulnerable save is greater than the save - pa.
    * If re roll is enabled on ALL dices, automatically disable reroll on the ones (hit dice and wound dice):
avoid double reroll)
    * A critical hit (resp. wound) is always a hit (resp. wound). For instance, if critical is set to 5+,
the opponent will be hit & wound AT MINIMUM at 5+.
"""
import os, sys
from typing import Union, Tuple
from os.path import dirname, abspath, join

# Go into root dir to enable imports
# ENV PATH
SRC_PATH = dirname(abspath(__file__))
# <absolute_path>/40k-dice-stats-computing/src/common/
ROOT_PATH = dirname(SRC_PATH)
# <absolute_path>/40k-dice-stats-computing/

# Modify Python path to enable import custom modules in root dir.
sys.path.append(ROOT_PATH)
# Assuming app is already working on src (see `buildozer.spec[source.dir]`) : else app bug
from common.dice import proba_dice, proba_rr_ones, proba_rr_all, add_sustain_hit, \
    get_wound_threshold, parse_expression, proba_crit
from common.utils import (nb_figs, crit, crit_wounds, weapon_a, hit_threshold, weapon_s, weapon_ap, weapon_d, bonus_wound, torrent,
                       rr_hit_ones, rr_hit_all, sustain_hit, lethal_hit, rr_wounds_ones, twin, devastating_wounds,
                       enemy_toughness, svg_enemy, svg_invul_enemy, fnp_enemy, enemy_hp, VERBOSE, fish)


def launch_workflow(nb_figs: int = nb_figs,
                    crit:int=crit,
                    crit_wounds: int = crit_wounds,
                    weapon_a:Union[str, int]=weapon_a,
                    hit_threshold:int=hit_threshold,
                    weapon_s:int=weapon_s,
                    weapon_ap:int=weapon_ap,
                    weapon_d:Union[str, int]=weapon_d,
                    bonus_wound:int=bonus_wound,
                    torrent:bool=torrent,
                    rr_hit_ones:bool=rr_hit_ones,
                    rr_hit_all:bool=rr_hit_all,
                    sustain_hit:Union[str, float]=sustain_hit,
                    lethal_hit:bool=lethal_hit,
                    rr_wounds_ones:bool=rr_wounds_ones,
                    twin:bool=twin,
                    devastating_wounds:bool=devastating_wounds,
                    fish: bool = fish,
                    enemy_toughness:int=enemy_toughness,
                    svg_enemy:int=svg_enemy,
                    svg_invul_enemy:int=svg_invul_enemy,
                    fnp_enemy:int=fnp_enemy,
                    enemy_hp:int=enemy_hp,
                    verbose:bool=VERBOSE) -> Tuple[float, float]:
    """
    Compute (average dead, remaining HP) based on statistics.

    :param nb_figs: Number of figurines attacking
    :param crit: Value of dice to get a critical (6 means crit at 6+)
    :param crit_wounds: Idem for wound roll
    :param weapon_a: Number of attackk of the weapon (ex: "2D6+1" or 3)
    :param hit_threshold: Hit capacity (3 means 3+)
    :param weapon_s: Weapon strenght
    :param weapon_ap: Armour piercing of the weapon (1 mean PA-1, 0 means no AP)
    :param weapon_d: Damage of the weapon (e.g. "D3+1" or 3)
    :param bonus_wound: Bonus wound (1 means +1 to wound, 0 means no bonus, -1 means malus of -1 to wound)
    :param torrent: If True, do not launch any hit dice
    :param rr_hit_ones: If True, reroll the one during the hit launch.
    :param rr_hit_all: If True, re-roll all failed hit
    :param sustain_hit: Set the sustain hit of the weapon (0 means no sustain hit) (e.g. "D3" or 2)
    :param lethal_hit: if True: enable lethal hit
    :param rr_wounds_ones: If True, re-roll the one during wound launch.
    :param twin: If True, reroll all failed wounds
    :param devastating_wounds: If True: enable devastating wounds (critical wounds raises mortal wounds)
    :param fish: If True, re-roll all dices except critical to enable lethal (if lethal), sustain (if sustain) or deva
    wound (if deva). Default False. Note that set to False if not possible to reroll dices (hits for lethal / sustain
    or wounds for deva).
    :param enemy_toughness: Endurance of the enemy
    :param svg_enemy: Save of the enemy (4 means 4+, 7 means no save)
    :param svg_invul_enemy: Invulnerable save of the enemy (4 means 4+, 7 means no save)
    :param fnp_enemy: Feel no Pain (FNP) (4 means 4+, 7 means no FNP), default 7
    :param enemy_hp: Health Point (hp) of the enemy
    :param verbose: Set to True to print debug elements

    :return: Tuple composed by:
        * enemy_dead: number of enemy dead
        * remaining_hp: remaining HP of a non dead enemy figurine
    """
    # ------------------------------------------------------------------------------
    # 0/ Init
    # ------------------------------------------------------------------------------
    # Checker
    # ---------------------
    if fnp_enemy is None:
        fnp_enemy = 7
    if svg_enemy is None:
        svg_enemy = 7
    if svg_invul_enemy is None:
        svg_invul_enemy = 7

    # 0.1/ Check incompatible bonuses
    # ------------------------------------------------------------------------------
    # If re roll is enabled on ALL dices, automatically disable reroll on the One
    if rr_hit_all:
        if verbose: print("[DEBUG]: Re-roll hit one disabled due to `rr_hit_all`=True (avoid double reroll)")
        rr_hit_ones = False

    # If torrent weapon, do not re-roll any hit dice
    if torrent:
        if verbose: print("[DEBUG]: Torrent weapon : do not re-roll any hit dice `rr_hit_all`=False and `rr_hit_ones`=False")
        rr_hit_all = False
        rr_hit_ones = False

    # Idem on wound dice
    if twin:
        if verbose: print("[DEBUG]: Re-roll wound one disabled due to `twin`=True avoid double reroll)")
        rr_wounds_ones = False

    # If weapon is not devastating wound: do not re-roll all dice to maximize devatating wounds
    if not devastating_wounds:
        re_roll_non_devastating_wound = False

    # Fishing (re-roll dices to search more criticals, to proc more deva / sustain / lethal)
    # ------------------------------
    fish_hits = False
    fish_wounds = False

    if fish:
        # Case re-roll hits: if impossible to re-roll OR no sustain neither lethal hit allowed
        if not (rr_hit_all or ((str(sustain_hit) != "0") and (not lethal_hit))):
            if verbose: print(f"[DEBUG]: Impossible to fish hits. One condition not respected between rr_hit ({rr_hit_all}), sustain ({sustain_hit}), lethal ({lethal_hit})")
        else:
            fish_hits = True
        # Case re-roll wounds: if impossible to rr wounds OR no deva wounds
        if not (twin and devastating_wounds):
            if verbose: print(
                f"[DEBUG]: Impossible to fish wounds. One condition not respected between rr_wounds ({twin}), deva wounds ({devastating_wounds})")
        else:
            fish_wounds = True

    # 0.2/ Init
    # ------------------------------------------------------------------------------
    # Compute wound threshold (incl. bonus)
    # ------------------------------------------------------------------------------
    # Determine the value of dice to wound enemy (comparing strengh and Toughness)
    wounds_threshold = get_wound_threshold(weapon_s=weapon_s, enemy_toughness=enemy_toughness)

    # Apply bonus / malus on wounds capability
    wounds_threshold = wounds_threshold - bonus_wound

    # Take into account crits (A critical hit/wound is always a hit/wound)
    # ------------------------------------------------------------------------------
    # A critical wound is always a wound
    wounds_threshold = min(crit_wounds, wounds_threshold)

    # A critical hit is always a hit
    hit_threshold = min(crit, hit_threshold)

    # Compute enemy save
    # ------------------------------------------------------------------------------
    # Apply AP
    svg_enemy = min(svg_enemy + weapon_ap, 7)

    if (svg_enemy > svg_invul_enemy):
        if verbose: print("[DEBUG]: Proc on invulnerable save")
        svg_enemy = svg_invul_enemy
        if (svg_invul_enemy > 6):
            if verbose: print("[DEBUG]: no save (!)")
            # NB: Pay attention, in the code, even if "no save", the filter is always applied (here filter dices < 7 = all dices)
            svg_enemy = 7
    # ------------------------------------------------------------------------------
    # 1/ Compute number of attack: nb figs * weapon_a
    # ------------------------------------------------------------------------------
    w_a = parse_expression(dice_expression=weapon_a)
    nb_attack = w_a * nb_figs

    # ------------------------------------------------------------------------------
    # 2/ hits
    # ------------------------------------------------------------------------------
    if torrent:
        if verbose: print("[DEBUG] Torrent weapon used")
        proba_hit = 1

    # If requested, re-roll the 1 (only)
    elif rr_hit_ones:
        if verbose: print("[DEBUG] Re-roll hit one")
        proba_hit = proba_rr_ones(hit_threshold)

    # If requested, re-roll all dices < the hit threshold
    elif rr_hit_all and (not fish_hits):
        if verbose: print("[DEBUG] Re-roll hit all")
        proba_hit = proba_rr_all(hit_threshold)

    else:
        proba_hit = proba_dice(dice_requested=hit_threshold)

    # 2.1/ FISH (special case)
    # ------------------------------
    nb_crit = proba_crit(crit=crit) * nb_attack


    if rr_hit_all and fish_hits:
        if verbose: print("[DEBUG] Fishing hits")
        # ROLL 1:
        # Re-roll all dices (`nb_attack`) except critical
        nb_non_critical_launch = nb_attack - nb_crit

        # ROLL 2:
        nb_crit += proba_crit(crit=crit) * nb_non_critical_launch
        nb_non_critical_launch = nb_attack - nb_crit  # make sure correct nb of crit removed from attack

        # REMAINING succeeded dices (lethal hits already droped)
        average_hit = proba_dice(dice_requested=hit_threshold) * nb_non_critical_launch
    else:
        average_hit = proba_hit * nb_attack

    # 2.2/ SUSTAIN
    # -------------------------
    sustain_additional_hit = 0
    if sustain_hit != 0:
        # Get the (eventually fished) sustain hits
        sustain_additional_hit = parse_expression(sustain_hit) * nb_crit

    # Add average nb of sustain
    average_hit += sustain_additional_hit

    # 2.3/ LETHAL
    # -------------------------
    # get lethal hit
    nb_lethal_hits = 0
    if lethal_hit:
        nb_lethal_hits = nb_crit
        if verbose: print(f"[DEBUG] Get {nb_lethal_hits} lethal hit")

    if not fish_hits:
        # remove lethal hits (do not count twice)
        average_hit = average_hit - nb_lethal_hits
        # already done if fish_hits = True
    if verbose: print(
        f"[DEBUG] At this stage, hit average: {average_hit}, including {sustain_additional_hit} hits comming from sustain hit")

    # ------------------------------------------------------------------------------
    # 3/ Wounds
    # -------------------------------------------
    # If requested, re-roll the 1 (only)
    if rr_wounds_ones:
        if verbose: print("[DEBUG] Re-roll wounds one")
        proba_w = proba_rr_ones(wounds_threshold)

    elif twin and not fish_wounds:
        if verbose: print("[DEBUG] Re-roll wounds all")
        proba_w = proba_rr_all(wounds_threshold)

    else:
        proba_w = proba_dice(dice_requested=wounds_threshold)

    nb_crit = proba_crit(crit=crit_wounds) * average_hit

    if (twin and fish_wounds and devastating_wounds):
        if verbose: print("[DEBUG] Fishing wounds")
        # Re-roll all dices (`average_hit`) except critical
        nb_non_critical_launch = average_hit - nb_crit

        # ROLL 2:
        nb_crit += proba_crit(crit=crit_wounds) * nb_non_critical_launch
        nb_non_critical_launch = average_hit - nb_crit  # make sure correct nb of crit removed from attack

        # REMAINING succeeded dices (deva wounds already droped)
        average_wounds = nb_lethal_hits + nb_non_critical_launch * proba_w
    else:
        # Success wounds
        average_wounds = nb_lethal_hits + average_hit * proba_w

    # get devastating wound
    nb_deva_w = 0

    if devastating_wounds:
        nb_deva_w = nb_crit
        if verbose: print(f"[DEBUG] Get {nb_deva_w} devastating wounds")

    if not fish_wounds:
        # remove devastating wounds from succeeded wounds (do not count twice)
        average_wounds = average_wounds - nb_deva_w
        # already done if fish_wounds = True

    if verbose: print(
        f"[DEBUG] At this stage, wounds average: {average_wounds}, including {nb_lethal_hits} lethal hits, and {nb_deva_w} devastating wounds")

    # ------------------------------------------------------------------------------
    # 4/ Save
    # ------------------------------------------------------------------------------
    # Get the number of FAILED save (succeed=False: we want to get dices inferior to a value)
    proba_failed_svg = proba_dice(dice_requested=svg_enemy, succeed=False)

    failed_svg = average_wounds * proba_failed_svg + nb_deva_w

    if verbose: print(f"[DEBUG] At this stage, average saves failed (without deva w.): {average_wounds * proba_failed_svg}")
    if verbose: print(f"[DEBUG] Average saves failed including deva wounds ({nb_deva_w:.2f}): {failed_svg}")

    # ------------------------------------------------------------------------------
    # 5/ Feel no pain and deads
    # ------------------------------------------------------------------------------
    # If failed_svg not int (e.g. 5.3), apply algo on int value
    failed_saved_int = int(failed_svg)  # ex: 5
    remaining_failed_saves = failed_svg - failed_saved_int  # ex: 0.3

    # Compute proba to fail feel no pain
    proba_fnp_failed = proba_dice(dice_requested=fnp_enemy, succeed=False)  # 1 if fnp_enemy=7

    # counter of deads
    enemy_dead = 0
    # Int changing during the loop. represent THE figurine with remaining hp
    remaining_hp = enemy_hp
    # Apply damage (ex: 1D6) and average fnp
    damage = parse_expression(weapon_d) * proba_fnp_failed  # ex: 2
    if verbose: print(f"Average damage: {damage} (including {fnp_enemy}+ feel no pain)")

    # Apply damages on `failed_saved_int` (int)
    # -------------------------------------
    # As it is an int, loop is possible

    # If there is saves failed
    if failed_saved_int > 0:
        for i, d in enumerate(range(failed_saved_int)):
            if damage >= remaining_hp:  # damage will kill the unit
                enemy_dead += 1
                remaining_hp = enemy_hp
            else:  # damage won't kill the unit
                remaining_hp -= damage

    # Apply damages on `remaining_failed_saves` (float)
    # -------------------------------------
    # As it is a float (<1), loop is not possible
    remaining_hp -= remaining_failed_saves * proba_fnp_failed

    # Get sure to avoid dumb results (e.g. remaining_failed_saves=0.99 > certainly more deads if sufficient damage)
    if remaining_hp < 0:
        remaining_hp = 0
        enemy_dead += 1

    if verbose:
        print(f"Nb dead (average): {enemy_dead}, 1 enemy remains with {remaining_hp}/{enemy_hp} HP")

    return enemy_dead, remaining_hp

if __name__ == "__main__":
    print(launch_workflow(verbose=True))