"""
Test module dice.py
"""

import pytest
import os, sys

# Go into root dir to enable imports
ROOT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../"

# Modify Python path to enable import custom modules in root dir.
sys.path.append(ROOT_DIR)

from src.dice import *


def test_parse_expression():
    with pytest.raises(ValueError):
        # Test input is str and not contains "D"
        parse_expression("aba")

    assert parse_expression("2D6+1") == 8  # 8
    assert parse_expression("D3") == 2  # 2
    assert parse_expression("2D3") == 4  # 4
    assert parse_expression("D3+1") == 3  # 3
    assert parse_expression("D6") == 3.5 # 3.5
    assert parse_expression("2D6") == 7  # 7
    assert parse_expression("D6+1") == 4.5  # 4.5

    assert parse_expression(3) == 3

def test_proba_dice():
    assert proba_dice(dice_requested=1) == 1
    assert proba_dice(dice_requested=2) == 5 / 6
    assert proba_dice(dice_requested=3) == 2 / 3
    assert proba_dice(dice_requested=4) == 1 / 2
    assert proba_dice(dice_requested=5) == 1 / 3
    assert proba_dice(dice_requested=6) == 1 / 6

def test_proba_rr_ones():
    assert pytest.approx(proba_rr_ones(dice_requested=3), 0.01) == 4/6 + (1/6) * (4/6)
    assert pytest.approx(proba_rr_ones(dice_requested=2), 0.01) == 5/6 + (1/6) * (5/6)

def test_proba_rr_all():
    assert pytest.approx(proba_rr_all(dice_requested=3), 0.01) == 8 / 9
    assert pytest.approx(proba_rr_all(dice_requested=4), 0.01) == 3 / 4
    assert pytest.approx(proba_rr_all(dice_requested=6), 0.01) == 1/6 + (5/6 * 1/6)

def test_add_sustain_hit():
    assert add_sustain_hit(2, 1) == 2  # 2
    assert add_sustain_hit(2, 4) == 1

def test_get_wound_threshold():
    assert get_wound_threshold(weapon_s=2, enemy_toughness=1) == 2  # s = 2* T
    assert get_wound_threshold(weapon_s=5, enemy_toughness=2) == 2  # s > 2* T
    assert get_wound_threshold(weapon_s=3, enemy_toughness=2) == 3  # T <= s < 2* T
    assert get_wound_threshold(weapon_s=2, enemy_toughness=2) == 4  # s = T
    assert get_wound_threshold(weapon_s=2, enemy_toughness=3) == 5  # (s < T) and (2 * s > T )
    assert get_wound_threshold(weapon_s=1, enemy_toughness=3) == 6  # 2 * s <= T

    assert get_wound_threshold(weapon_s=4, enemy_toughness=5) == 5


