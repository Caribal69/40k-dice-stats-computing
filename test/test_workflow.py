"""
Test if the workflow is not broken.

By default, this script works if the params in utils.py are all set to False.

For coherence with tox and pytest, name each new function with `test_<something>` > these functions will be launch
at each tox init.
"""

import pytest
import sys
import os

# Go into root dir to enable imports
ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../"

# Modify Python path to enable import custom modules in root dir.
sys.path.append(ROOT_DIR)

from src.common.workflow import launch_workflow
from src.common.dice import compute_average_enemy_dead

# UTILS : WRAPPERS
# ---------------------------------------------------------------------
def launch(nb_figs=10,
           weapon_a=1,
           weapon_s=4,
           weapon_ap=0,
           hit_threshold=4,
           weapon_d=1,
           enemy_toughness=4,
           svg_enemy=4,
           svg_invul_enemy=7,  # no save
           fnp_enemy=7,  # no fnp
           enemy_hp=1,
           sustain_hit=0,
           crit=6,
           **kwargs):
    """
    A wrapper function permitting to test if the values given by workflow is compliant with manually computed statistics
    (especially regarding average results).

    :param kwargs: Any argument of function `workflow.launch_workflow` in:
    * torrent
    * rr_hit_ones
    * rr_hit_all
    * sustain_hit
    * lethal_hit
    * rr_wounds_ones
    * twin
    * devastating_wounds

    :return: Average lost HP of opponent enemy_dead+(enemy_hp-remaining_hp)
    """

    enemy_dead, remaining_hp = launch_workflow(nb_figs=nb_figs,
                                               weapon_a=weapon_a,
                                               weapon_s=weapon_s,
                                               enemy_toughness=enemy_toughness,
                                               bonus_wound=0,
                                               svg_enemy=svg_enemy,
                                               weapon_ap=weapon_ap,
                                               svg_invul_enemy=svg_invul_enemy,
                                               hit_threshold=hit_threshold,
                                               crit=crit,
                                               weapon_d=weapon_d,
                                               fnp_enemy=fnp_enemy,
                                               enemy_hp=enemy_hp,
                                               sustain_hit=sustain_hit,
                                               verbose=True,
                                               **kwargs,
                                               )
    # return lost models
    return compute_average_enemy_dead(enemy_dead=enemy_dead, remaining_hp=remaining_hp, enemy_hp=enemy_hp)


def compare_to_expected(expected: float, **kwargs):
    """"
    Test a new configuration of `launch_workflow`. Compare it to `expected` value.

    Note that, due to rounding, results are tested with a tolerance of 0.01.

    :param expected: Expected value of result (average of damages)
    :param kwargs: Any argument of `launch` function.
    """
    print("-" * 20)
    r = launch(**kwargs)
    print(f"Total average lost figurines: {r}")
    print(f"Expected (average) value: {expected}")
    # Assert equal at 0.1
    assert pytest.approx(r, 0.1) == expected


# LAUNCH TESTS
# -----------------------------------------------------------------------------------
def test_normal_shot():
    # 10 shots, skill = 4+, wound = 4+, armour = 4+
    # Result (expected): 10*0.5*0.5*0.5 =~ 0.125
    print("Normal shot:")

    compare_to_expected(expected=10 * 0.5 * 0.5 * 0.5)


def test_reroll_hit_dices():
    # 10 shots, skill = 4+ (with re-roll: 3/4 chances instead of 1/2), wound = 4+, armour = 4+
    # Result (expected): 10*0.75*0.5*0.5 =~ 0.125
    print("Re roll hit dices")

    compare_to_expected(expected=10 * 0.75 * 0.5 * 0.5, rr_hit_all=True)

def test_reroll_wounds():
    # expect same results
    print("Re-roll wound dice")

    compare_to_expected(expected=10 * 0.75 * 0.5 * 0.5, twin=True)

    # 10 shots, skill = 3+, wound = 5+
    # enemy = T5 / S4 (wound 5+), svg 3+
    # Result (expected): 10*2/3*1/3*1/3 =~ 0.74 > no rr
    # Result (expected): 10 * 2/3 * (1/3 + 1/9) * 1/3 =~ 0.98 > with twin

    compare_to_expected(expected=10 * 2 / 3 * (1 / 3 + 1 / 9) * 1 / 3,
                        enemy_toughness=5,
                        svg_enemy=2,
                        weapon_ap=1,
                        twin=True)
def test_rr_hit_ones():
    # 10 shots, skill = 4+ (with re-roll ones: 0.58 chances instead of 0.5), wound = 4+, armour = 4+
    # Result (expected): 10*0.58*0.5*0.5 =~ 0.125
    print("Re roll hit ones")

    compare_to_expected(expected=10 * 0.58 * 0.5 * 0.5, rr_hit_ones=True)

def test_rr_wounds_ones():
    # Same result
    print("Re roll wound ones")

    compare_to_expected(expected=10 * 0.58 * 0.5 * 0.5, rr_wounds_ones=True)

def test_lethal_hit():
    # 10 shots, skill = 4+ (with 6 = automatic wound), wound = 4+, armour = 4+
    # Result (expected): 10*( (2/6 * 1/2 * 1/2) + (1/6 * 1/2)) = 1.6
    print("Lethal hit")

    compare_to_expected(expected=10 * (((2 / 6) * 0.5 * 0.5) + ((1 / 6) * 1 / 2)), lethal_hit=True)


def test_devastating_wounds():
    # 10 shots, skill = 4+ wound = 4+ (with 6 = no save), armour = 4+
    # Result (expected): 10*( (1/2 * 2/6 * 1/2) + (1/2 * 1/6)) = 1.6
    # Same result expected (as save = capacity to wound = capacity to hit)

    print("devastating_wound hit")
    compare_to_expected(expected=10 * (((2 / 6) * 0.5 * 0.5) + ((1 / 6) * 1 / 2)), devastating_wounds=True)


def test_sustain_hit():
    # 10 shots, skill = 4+ (with 6 = 1 more hit), wound = 4+, armour = 4+
    # Result (expected): 10*((0.5 * 0.5 * 0.5) + (1/6 * 2 * 0.5 * 0.5)) = 2.08
    #   - 10*((0.5 * 0.5 * 0.5): normal hits
    #   - (1/6 * 2 * 0.5 * 0.5): proportion of sustain hits (already hit: only round wounds + saves)
    # Same result expected (as save = capacity to wound = capacity to hit)

    print("Sustain hit 2")
    compare_to_expected(expected=10 * ((0.5 * 0.5 * 0.5) + (1 / 6 * 2 * 0.5 * 0.5)), sustain_hit=2)


def test_torrent():
    # 10 shots, skill = 1+ (torrent), wound = 4+, armour = 4+
    # Result (expected): 10 * 0.5 * 0.5 = 2.5

    print("torrent")
    compare_to_expected(expected=10 * 0.5 * 0.5, torrent=True)


def test_torrent_twin():
    # 10 shots, skill = 1+ (torrent), wound = 4+ (re-roll), armour = 4+
    # Result (expected): 10 * (0.5 + 1/4) * 0.5 = 3.75

    print("torrent and twin")
    compare_to_expected(expected=10 * (0.5 + 1 / 4) * 0.5, torrent=True, twin=True)

    # 10 shots, skill = 3+ (torrent), wound = 5+ (re-roll), armour = 3+
    # Result (expected): 10 * (1/3 + 2/9) * 1/3 = 1.85

    compare_to_expected(expected=10 * (1 / 3 + 2 / 9) * 1 / 3,
                        hit_threshold=3,
                        weapon_s=4,
                        weapon_ap=1,
                        enemy_hp=1,
                        enemy_toughness=5,
                        svg_enemy=2,
                        torrent=True,
                        twin=True,
                        )


def test_ap():
    # 10 shots, skill = 4+, wound = 4+, armour = 5+ (instead of 4+)
    # Result (expected): 10*(0.5*0.5*2/3) = 1.6
    # Same result expected (as save = capacity to wound = capacity to hit)

    print("AP 1")
    compare_to_expected(expected=10 * (0.5 * 0.5 * 2 / 3), weapon_ap=1)


def test_S_sup_T():
    # F > T (wound at 3+)

    # 10 shots, skill = 4+, wound = 3+, armour = 4+
    # Result (expected): 10*(0.5*2/3*0.5) = 1.6
    # Same result expected (as save = capacity to wound = capacity to hit)

    print("Strenght > Toughtness (wound at 3+)")
    compare_to_expected(expected=10 * (0.5 * 2 / 3 * 0.5), weapon_s=5)


def test_S_eq_double_T():
    # F = 2 * T (wound at 2+)

    # 10 shots, skill = 4+, wound = 2+, armour = 4+
    # Result (expected): 10*(0.5*5/6*0.5) = 2.08
    # Same result expected (as save = capacity to wound = capacity to hit)

    print("Strenght = 2 *  Toughtness (wound at 2+)")

    compare_to_expected(expected=10 * (0.5 * 5 / 6 * 0.5), weapon_s=8)


def test_S_sup_double_T():
    # F > 2*T (wound at 2+)

    # Same result expected

    print("Strenght > 2 *  Toughtness (wound at 2+)")

    compare_to_expected(expected=10 * (0.5 * 5 / 6 * 0.5), weapon_s=10)


def test_profile_1():
    # Other profile

    # 30 shots, skill = 2+, wound = 3+, armour = 5+ (ap= 2, save=3+)
    # Result (expected): 10*30*(5/6 * 4/6 * 4/6) = 11.1
    # nb_fig * weapon_a * (proba hit (2+) * proba w (3+) * save (5+))
    # Same result expected (as save = capacity to wound = capacity to hit)

    print("Other profile (2+>3+>5+)")

    compare_to_expected(expected=10 * 30 * (5 / 6 * 4 / 6 * 4 / 6),
                        weapon_a=30,
                        weapon_s=6,
                        weapon_ap=2,
                        hit_threshold=2,
                        weapon_d=1,
                        enemy_toughness=4,
                        svg_enemy=3,
                        )


def test_critical():
    # Test critical (5+) and F << E

    print("Critical 5+ (4+ > 5+ > 2+)")
    compare_to_expected(expected=10 * 20 * (0.5 * 1 / 3 * 1 / 6),
                        weapon_a=20,
                        weapon_s=5,
                        hit_threshold=4,
                        enemy_toughness=9,
                        svg_enemy=2,
                        crit=5,
                        )

def test_fish_hit_impossible():
    """
    Test cases when fish hit is not possible
    """
    # Test no fish
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0)
    print("4+ > 4+ > 4+")
    compare_to_expected(expected=10 * (0.5 * 0.5 * 0.5),
                        crit=6,
                        fish=False,
                        rr_hit_all=False,
                        lethal_hit=False,
                        sustain_hit=0,
                        )

    # Test fish hit impossible (rr hit but no lethal neither sustain)
    compare_to_expected(expected=10 * (0.5 * 0.5 * 0.5),
                        crit=6,
                        fish=True,
                        rr_hit_all=False,
                        lethal_hit=False,
                        sustain_hit=0,
                        )

    # Test fish hit impossible (lethal but no rr hit)
    compare_to_expected(expected=10 * ( (0.5 - 1 / 6) * 0.5 * 0.5 + (1 / 6) * 0.5),
                        crit=6,
                        fish=True,
                        rr_hit_all=False,
                        lethal_hit=True,
                        sustain_hit=0,
                        )

    # Test fish hit impossible (sustain but no rr hit)
    compare_to_expected(expected=10 * (0.5 + 1/6) * 0.5 * 0.5,
                        crit=6,
                        fish=True,
                        rr_hit_all=False,
                        lethal_hit=False,
                        sustain_hit=1,
                        )

    # Test fish hit impossible (sustain AND lethal but no rr hit)
    compare_to_expected(expected=10 * (0.5 * 0.5 * 0.5 + (1 / 6) * 0.5),
                        crit=6,
                        fish=True,
                        rr_hit_all=False,
                        lethal_hit=True,
                        sustain_hit=1,
                        )


def test_fish_wound_impossible():
    """
    Test cases when fish wound is not possible
    """
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0)

    # Test fish wound impossible (no deva nor rr wound)
    compare_to_expected(expected=10 * 0.5 * 0.5 * 0.5,
                        crit=6,
                        fish=True,
                        twin=False,
                        devastating_wounds=False
                        )

    # Test fish wound impossible (deva but no rr wound)
    compare_to_expected(expected=10 * 0.5 * (2/6 * 0.5 + 1/6), # 10 * 0.5 * ((0.5 - 1/6) * 0.5 + 1/6),
                        crit=6,
                        fish=True,
                        twin=False,
                        devastating_wounds=True
                        )

def test_fish_deva_wounds():
    """
    Test fishing devastating wounds when crit at 6+ or 5+ (crit is for HIT only, not wound)
    """
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0) deva wound

    nb_deva = (1/6 + (1 - 1/6) * 1/6)
    compare_to_expected(expected=10*0.5*( (1-nb_deva) * 0.5 * 0.5 + nb_deva),
                        crit=6,
                        fish=True,
                        twin=True,
                        devastating_wounds=True
                        )

    # Crit 5+
    compare_to_expected(expected=10*0.5*( (1-nb_deva) * 0.5 * 0.5 + nb_deva),
                        crit=5,
                        fish=True,
                        twin=True,
                        devastating_wounds=True
                        )
def test_fish_lethal_hits():
    """
    Test fishing lethal hits when crit at 6+ or 5+
    """
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0) lethal hit
    nb_lethal = (1/6 + (1 - 1/6) * 1/6)
    compare_to_expected(expected=10 * (nb_lethal + (1 - nb_lethal) * 0.5 * 0.5) * 0.5,
                        crit=6,
                        fish=True,
                        rr_hit_all=True,
                        lethal_hit=True,
                        sustain_hit=0,
                        )
    # Crit 5+
    nb_lethal = (2/6 + (1 - 2/6) * 2/6)
    compare_to_expected(expected=10 * (nb_lethal + (1-nb_lethal)*0.5*0.5)*0.5,
                        crit=5,
                        fish=True,
                        rr_hit_all=True,
                        lethal_hit=True,
                        sustain_hit=0,
                        )


def test_fish_sustain():
    """
    Test fishing sustain hits when crit at 6+ or 5+
    """
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0) sustain hit 1
    nb_sustain = (1/6 + (1 - 1/6) * 1/6)
    compare_to_expected(expected=10 * 0.5 * (1 + nb_sustain) * 0.5 * 0.5,
                        crit=6,
                        fish=True,
                        rr_hit_all=True,
                        lethal_hit=False,
                        sustain_hit=1,
                        )
    # Crit 5+
    nb_sustain = (2/6 + (1 - 2/6) * 1/6)
    compare_to_expected(expected=10 * 0.5 * (1 + nb_sustain) * 0.5 * 0.5,
                        crit=5,
                        fish=True,
                        rr_hit_all=True,
                        lethal_hit=False,
                        sustain_hit=1,
                        )
def test_fish_lethal_sustain():
    """
    Test fishing sustain and lethal hits  when crit at 6+ or 5+
    """
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0) sustain hit 1 / lethal hit
    nb_sustain = (1/6 + (1 - 1/6) * 1/6)
    nb_lethal = (1/6 + (1 - 1/6) * 1/6)
    compare_to_expected(expected=10 * (((1 - nb_lethal) * 0.5) + nb_sustain) * 0.5 * 0.5 + 10 * nb_lethal * 0.5,
                        crit=6,
                        fish=True,
                        rr_hit_all=True,
                        lethal_hit=True,
                        sustain_hit=1,
                        )

    # Crit 5+
    nb_sustain = (2/6 + (1 - 2/6) * 2/6)
    nb_lethal = (2/6 + (1 - 2/6) * 2/6)
    compare_to_expected(expected=10 * (((1 - nb_lethal) * 0.5) + nb_sustain) * 0.5 * 0.5 + 10 * nb_lethal * 0.5,
                        crit=5,
                        fish=True,
                        rr_hit_all=True,
                        lethal_hit=True,
                        sustain_hit=1,
                        )
def test_fish_all():
    """
    Test fishing:
    * lethal + deva (we consider the two are fished: hit + wounds)
    * sustain + deva
    * lethal + sustain + deva

    When critical = 6+ or 5+
    """
    # 10 attacks, 4+ hit, 4+ wound, 4+ save (AP=0)
    nb_deva = (1 / 6 + (1 - 1 / 6) * 1 / 6)
    nb_lethal = (1 / 6 + (1 - 1 / 6) * 1 / 6)
    nb_sustain = (1 / 6 + (1 - 1 / 6) * 1 / 6)

    # lethal hit + deva wound
    compare_to_expected(expected=10 * 0.5 * (1-nb_lethal) * ( (1-nb_deva)*0.5*0.5 + nb_deva) + 10 * nb_lethal * 0.5,
                        crit=6,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=True,
                        sustain_hit=0,
                        devastating_wounds=True,
                        )

    # sustain hit + deva wound
    compare_to_expected(expected=10 * 0.5 * (1 + nb_sustain) * ( (1 - nb_deva) * 0.5 * 0.5 + nb_deva),
                        crit=6,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=False,
                        sustain_hit=1,
                        devastating_wounds=True,
                        )

    # lethal hit + sustain hit + deva wound
    compare_to_expected(expected=10 * ( (((1 - nb_lethal) * 0.5 * (1 - nb_deva)) + nb_sustain) * 0.5 * 0.5) + 10 * 0.5 * (1+nb_sustain) * nb_deva + 10 * nb_lethal * 0.5,
                        crit=6,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=True,
                        sustain_hit=1,
                        devastating_wounds=True,
                        )

    # crit 5+ (wound AND hit)
    # --------
    nb_deva = (2 / 6 + (1 - 2 / 6) * 2 / 6)
    nb_lethal = (2 / 6 + (1 - 2 / 6) * 2 / 6)
    nb_sustain = (2 / 6 + (1 - 2 / 6) * 2 / 6)

    # lethal hit + deva wound
    compare_to_expected(expected=10 * 0.5 * (1-nb_lethal) * ( (1-nb_deva)*0.5*0.5 + nb_deva) + 10 * nb_lethal * 0.5,
                        crit=5,
                        crit_wounds=5,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=True,
                        sustain_hit=0,
                        devastating_wounds=True,
                        )
    # sustain hit + deva wound
    compare_to_expected(expected=10 * 0.5 * (1 + nb_sustain) * ( (1 - nb_deva) * 0.5 * 0.5 + nb_deva),
                        crit=5,
                        crit_wounds=5,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=False,
                        sustain_hit=1,
                        devastating_wounds=True,
                        )
    # lethal hit + sustain hit + deva wound
    compare_to_expected(expected=10 * ( (((1 - nb_lethal) * 0.5 * (1 - nb_deva)) + nb_sustain) * 0.5 * 0.5) + 10 * 0.5 * (1+nb_sustain) * nb_deva + 10 * nb_lethal * 0.5,
                        crit=5,
                        crit_wounds=5,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=True,
                        sustain_hit=1,
                        devastating_wounds=True,
                        )

def test_fish_crit_hit_not_wound():
    """
    Test fishing:
    * lethal + deva (we consider the two are fished: hit + wounds)
    * sustain + deva
    * lethal + sustain + deva

    When critical hit = 5+ and critical w = 6+
    """
    # crit 5+ HIT
    # --------
    nb_lethal = (2 / 6 + (1 - 2 / 6) * 2 / 6)
    nb_sustain = (2 / 6 + (1 - 2 / 6) * 2 / 6)

    # crit 6+ wound
    nb_deva = (1 / 6 + (1 - 1 / 6) * 1 / 6)

    # lethal hit + deva wound
    compare_to_expected(expected=10 * 0.5 * (1-nb_lethal) * ( (1-nb_deva)*0.5*0.5 + nb_deva) + 10 * nb_lethal * 0.5,
                        crit=5,
                        crit_wounds=6,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=True,
                        sustain_hit=0,
                        devastating_wounds=True,
                        )
    # sustain hit + deva wound
    compare_to_expected(expected=10 * 0.5 * (1 + nb_sustain) * ( (1 - nb_deva) * 0.5 * 0.5 + nb_deva),
                        crit=5,
                        crit_wounds=6,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=False,
                        sustain_hit=1,
                        devastating_wounds=True,
                        )
    # lethal hit + sustain hit + deva wound
    compare_to_expected(expected=10 * ( (((1 - nb_lethal) * 0.5 * (1 - nb_deva)) + nb_sustain) * 0.5 * 0.5) + 10 * 0.5 * (1+nb_sustain) * nb_deva + 10 * nb_lethal * 0.5,
                        crit=5,
                        crit_wounds=6,
                        fish=True,
                        rr_hit_all=True,
                        twin=True,
                        lethal_hit=True,
                        sustain_hit=1,
                        devastating_wounds=True,
                        )



def test_no_save():
    # 10 shots, skill = 4+ wound = 4+, armour = 7+
    print("No save")
    compare_to_expected(expected=10*0.5*0.5, svg_enemy=7)

    compare_to_expected(expected=10 * 0.5 * 0.5, weapon_ap=4, svg_enemy=6, svg_invul_enemy=7)

def test_svg_better_than_svg_invu():
    # 10 shots, skill = 4+ wound = 4+, armour = 4+
    print("test (svg_enemy > svg_invul_enemy)")
    compare_to_expected(expected=10*0.5*0.5*0.5, svg_enemy=4, svg_invul_enemy=5)

def test_proc_svg_invu():
    # 10 shots, skill = 4+ wound = 4+, armour = 4+
    print("test (svg_enemy > svg_invul_enemy)")
    compare_to_expected(expected=10*0.5*0.5*0.5, weapon_ap=2, svg_enemy=3, svg_invul_enemy=4)

def test_remaining_hp_negative():
    # 6 shots, torrent, wound = 2+, no armour, dmg 3 (expect 5 wounds)
    #  4 HP per ennemy, expect 2 deads + 1 with 1 hp = 2.75 dead in avg
    print("test remaining_hp < 0")
    compare_to_expected(expected=2.75, nb_figs=6, enemy_hp=4, weapon_d=3, torrent=True, weapon_s=40, svg_enemy=7)


if __name__ == "__main__":

    import inspect
    import sys

    # test_normal_shot()
    # test_reroll_hit_dices()
    # test_reroll_wounds()
    # test_lethal_hit()
    # test_devastating_wounds()
    # test_sustain_hit()
    # test_ap()
    # test_S_sup_T()
    # test_S_eq_double_T()
    # test_S_sup_double_T()
    # test_profile_1()
    # test_critical()

    # Run all functions of the module (doc here: https://stackoverflow.com/questions/28643534/is-there-a-way-in-python-to-execute-all-functions-in-a-file-without-explicitly-c).
    mod = sys.modules[__name__]
    all_functions = inspect.getmembers(mod, inspect.isfunction)
    for key, value in all_functions:
        if str(inspect.signature(value)) == "()":
            value()
