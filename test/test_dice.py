"""
Test module dice.py
"""

import pytest
import os, sys

# Go into root dir to enable imports
ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../"

# Modify Python path to enable import custom modules in root dir.
sys.path.append(ROOT_DIR)

from src.common.dice import *
from src.common.dice import _parse_str_expression

def test_parse_str_expression():
    assert _parse_str_expression(2) ==  DiceExpression(nb_dice=0, dice_face=6, bonus=2)
    assert _parse_str_expression("d6") == DiceExpression(nb_dice=1, dice_face=6, bonus=0)
    assert _parse_str_expression("d6+1") == DiceExpression(nb_dice=1, dice_face=6, bonus=1)
    assert _parse_str_expression("2d6") == DiceExpression(nb_dice=2, dice_face=6, bonus=0)
    assert _parse_str_expression("2d6+1") == DiceExpression(nb_dice=2, dice_face=6, bonus=1)

def test_parse_expression():
    with pytest.raises(ValueError):
        # Test input is str and not contains "D"
        parse_expression("aba")
    with pytest.raises(ValueError):
        # Test input is not str and not contains "D"
        parse_expression({"a": "b"})
    with pytest.raises(ValueError):
        # Test input is not str and does contains "D"
        parse_expression({"aD": "b"})

    assert parse_expression("2D6+1") == 8  # 8
    assert parse_expression("D3") == 2  # 2
    assert parse_expression("2D3") == 4  # 4
    assert parse_expression("D3+1") == 3  # 3
    assert parse_expression("D6") == 3.5 # 3.5
    assert parse_expression("2D6") == 7  # 7
    assert parse_expression("D6+1") == 4.5  # 4.5

    # Lower case
    assert parse_expression("2d6+1") == 8  # 8
    assert parse_expression("d3") == 2  # 2
    assert parse_expression("2d3") == 4  # 4
    assert parse_expression("d3+1") == 3  # 3
    assert parse_expression("d6") == 3.5 # 3.5
    assert parse_expression("2d6") == 7  # 7
    assert parse_expression("d6+1") == 4.5  # 4.5

    assert parse_expression(3) == 3

def test_proba_dice():
    assert proba_dice(dice_requested=1) == 1
    assert proba_dice(dice_requested=2) == 5 / 6
    assert proba_dice(dice_requested=3) == 2 / 3
    assert proba_dice(dice_requested=4) == 1 / 2
    assert proba_dice(dice_requested=5) == 1 / 3
    assert proba_dice(dice_requested=6) == 1 / 6

def test_proba_rr_ones():
    assert pytest.approx(proba_rr_ones(dice_requested=6), 0.01) == 1/6 + (1/6) * (1/6)
    assert pytest.approx(proba_rr_ones(dice_requested=5), 0.01) == 2/6 + (1/6) * (2/6)
    assert pytest.approx(proba_rr_ones(dice_requested=4), 0.01) == 3/6 + (1/6) * (3/6)
    assert pytest.approx(proba_rr_ones(dice_requested=3), 0.01) == 4/6 + (1/6) * (4/6)
    assert pytest.approx(proba_rr_ones(dice_requested=2), 0.01) == 5/6 + (1/6) * (5/6)

def test_proba_rr_all():
    assert pytest.approx(proba_rr_all(dice_requested=2), 0.01) == (5 / 6) + (1/6)*(5/6)  # 2+ reroll
    assert pytest.approx(proba_rr_all(dice_requested=3), 0.01) == 8 / 9  # 3+ reroll
    assert pytest.approx(proba_rr_all(dice_requested=4), 0.01) == 3 / 4  # 4+ reroll
    assert pytest.approx(proba_rr_all(dice_requested=5), 0.01) == 2/6 + (4/6) * (2/6)  # 5+ reroll
    assert pytest.approx(proba_rr_all(dice_requested=6), 0.01) == 1/6 + (5/6 * 1/6)  # 6+  reroll

def test_add_sustain_hit():
    assert add_sustain_hit(2, 1) == 2  # 2
    assert add_sustain_hit(2, 4) == 1
    assert add_sustain_hit(2, 6) == 2*1/6
    assert add_sustain_hit(1, 5) == 1*2/6

def test_get_wound_threshold():
    assert get_wound_threshold(weapon_s=2, enemy_toughness=1) == 2  # s = 2* T
    assert get_wound_threshold(weapon_s=5, enemy_toughness=2) == 2  # s > 2* T
    assert get_wound_threshold(weapon_s=3, enemy_toughness=2) == 3  # T <= s < 2* T
    assert get_wound_threshold(weapon_s=2, enemy_toughness=2) == 4  # s = T
    assert get_wound_threshold(weapon_s=2, enemy_toughness=3) == 5  # (s < T) and (2 * s > T )
    assert get_wound_threshold(weapon_s=1, enemy_toughness=3) == 6  # 2 * s <= T

    assert get_wound_threshold(weapon_s=4, enemy_toughness=5) == 5


