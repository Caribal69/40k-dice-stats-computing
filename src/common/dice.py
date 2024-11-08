"""
A set of utils functions to compute probability, parse expressions, ...

Terminology:
* function starting with `proba`: compute a probability (0 < proba < 1)
* function starting with `add`: result to be added to a `proba` function

"""
from dataclasses import dataclass
from typing import Union

@dataclass
class DiceExpression:
    """
    This object stores the dice expressed as "complex expressions"
    Example: "2D6+1" --> DiceExpression(nb_dice=2, dice_face=6, bonus=1)
    """
    nb_dice: int
    dice_face: int
    bonus: int


def parse_expression(dice_expression: Union[str, int]) -> float:
    """
    Parse `dice_expression` into average result. Contains checkers.

    Exemples:
    * dice_expression = "2D6+1" or "2d6+1"--> result =  8 (average value of 2D6+1)
    * dice_expression = "D3" or "d3"--> result =  2 (average value of D3)
    * dice_expression = 3 --> result = 3

    :param dice_expression: str containing an expression to parse (ex: "2D6+1") or int
    :return: Average result of `dice_expression`

    :raises:
    * ValueError: `dice_expression` is str not containing "D" or "d"
    * ValueError: `dice_expression` not str or number
    """
    # Get sure "D" instead of "d"
    dice_expression = str(dice_expression).upper()

    # a) regular situation (int)
    try:
        r = int(dice_expression)  # ex: 3

    except ValueError:

        # b) parse (if dice_expression = "ND6+X", or "ND3+X")
        if (type(dice_expression) == str) and "D" in dice_expression:  # ex: A = 2D3

            r = _define_average_launch(dice_expression=dice_expression) # ex 3.5

        elif (type(dice_expression) == str) and "D" not in dice_expression:
            raise ValueError(f"Value have wrong format: A={dice_expression}, expected <some number>D<3 or 6> (e.g. 1D6)")
        else:
            ValueError(f"Value have wrong format: A={dice_expression}, expected format integer or <some number>D<3 or 6> (e.g. 1D6)")

    return r

def _parse_str_expression(dice_expression: str) -> DiceExpression:
    """
    Parse `dice_expression` into comprehensive result.

    Exemples:
    * dice_expression = "2D6+1" or "2d6+1"--> result =  8 (average value of 2D6+1)
    * dice_expression = "D3" or "d3"--> result =  2 (average value of D3)

    :param dice_expression: str containing an expression to parse (ex: 2D6+1)
    :return: `DiceExpression` containing ll relevant infos.

    NB: this function does NOT contain any check for optimality reason (check is done one single time, this
    function shall be called many times).
    """
    # Get sure "D" instead of "d"
    dice_expression = str(dice_expression).upper()

    s1 = dice_expression.split("D")
    # ex: "2D6+1" -> ['2', '6+1']

    if s1[0] == "":  # ex: "D3+1" -> s1 = ""
        nb_dice = 1
    else:
        nb_dice = int(s1[0])  # ex: 2

    if len(s1) == 1:  # ex: dice_expression="2"
        return DiceExpression(nb_dice=0, dice_face=6, bonus=nb_dice)
    elif len(s1) == 2:  # # ex: dice_expression="2D6+1"
        s2 = s1[1].split("+") # ex: "6+1"

        dice_face = int(s2[0])  # ex: 6

        bonus = 0
        if len(s2) == 2:
            bonus = int(s2[1])  # ex: 1

        return DiceExpression(nb_dice=nb_dice, dice_face=dice_face, bonus=bonus)


def _define_average_launch(dice_expression: str) -> float:
    """
    Define the average result of `dice_expression`.

    Exemple: dice_expression = 2D6+1 --> result =  2*3.5+1 = 8
    (because average result on one dice is 3,5)

    :param dice_expression: str containing an expression to parse (ex: "2D6+1")
    :return: Average result of `dice`
    """
    d = _parse_str_expression(dice_expression)
    # ex: DiceExpression(nb_dice=2, dice_face=6, bonus=1)

    # Average value of one dice = (the highest value + 1) / 2
    average_value_one_dice = (d.dice_face + 1) / 2
    # ex: 3.5 is the average result of 1D6 dice
    # ex: 2 is the average result of 1D3 dice
    return d.nb_dice * average_value_one_dice + d.bonus
def proba_dice(dice_requested: int, succeed=True) -> float:
    """
    Get the probability to succeed in having more (or equal) than `dice_requested` on a 6 face launch (case
    `succeed =True`). E.g. dice_requested=3 > probability 3+ > result = 2/3

    If succeed if `False`, return probability to fail to have more than `dice_requested`+ (or, in other terms, probab
     to have stricltly less than `dice_requested`+.

    :param dice_requested: Dice value requested. 3 means 3+
    :param succeed: Bool indicating if (case True) probability of success (i.e. proba to get dice >= dice_request)
    :return: Probability of success (0<= float <= 1)
    """
    # Probability to get a n+
    if succeed:
        return (7-dice_requested)/6
    else:
        return (dice_requested-1)/6


def proba_crit(crit: int) -> float:
    """
    Compute proba to get a critical.

    :param crit: Dice value to get a crit (6 means 6+)
    :return: Probability to get a crit (0<= float <= 1)
    """
    return proba_dice(dice_requested=crit, succeed=True)


# Proba if re-roll 1
def proba_rr_ones(dice_requested:int) -> float:
    """
    Get the probability to succeed in having more (or equal) than `dice_requested` on a 6 face launch
    Ones are re-roll.

    :param dice_requested: Dice value requested. 3 means 3+
    :return: Probability of success (0<= float <= 1)
    """
    proba = proba_dice(dice_requested)
    return proba + (1/6) * proba

# proba if rr all
def proba_rr_all(dice_requested:int) -> float:
    """
    Get the probability to succeed in having more (or equal) than `dice_requested` on a 6 face launch
    All dices are re-roll.

    :param dice_requested: Dice value requested. 3 means 3+
    :return: Probability of success (0<= float <= 1)
    """
    proba = proba_dice(dice_requested)
    return proba + proba*proba_dice(dice_requested, succeed=False)

# additional proba if sustain hit (to be added to proba)
def add_sustain_hit(sustain: float, crit: int=6) -> float:
    """
    Number of additional attack (on average). Compute chance of sustain hit.

    :param sustain: bonus of hit. Already parsed.
    :param crit: value of the crit (6 means 6+)
    :return: Additional probability of success (0<= float <= 1)
    """
    return sustain * proba_crit(crit=crit)

def get_wound_threshold(weapon_s: int, enemy_toughness: int) -> int:
    """
    Compare strength (`weapon_s`) versus toughness (`enemy_toughness`),
     and get the value of dice to succeed a wound.

    :param weapon_s: Strength of the weapon
    :param enemy_toughness: toughness of the enemy

    :return: Dice value (e.g. 4 means 4+) to wound enemy.
    """
    if weapon_s >= 2 * enemy_toughness:
        wounds_threshold = 2  # 2+

    elif (weapon_s > enemy_toughness) and (weapon_s <= 2 * enemy_toughness):
        wounds_threshold = 3  # 3+

    elif enemy_toughness == weapon_s:
        wounds_threshold = 4  # 4+

    elif (weapon_s < enemy_toughness) and (2 * weapon_s >= enemy_toughness):
        wounds_threshold = 5  # 5+

    elif (2 * weapon_s) < enemy_toughness:
        wounds_threshold = 6  # 6+

    return wounds_threshold

def compute_average_enemy_dead(enemy_dead: float, remaining_hp: float, enemy_hp: int) -> float:
    """
    Compute the average number of enemy lost from remaining hp. Useful for large mono-HP squad.

    In our computation, we have:
    * enemy_dead: average nb of dead figurine after an attack
    * remaining_hp: number of HP remaining of the figurine not dead

    :param enemy_dead: Result from `src.workflow.launch_workflow[0]`
    :param remaining_hp: Result from `src.workflow.launch_workflow[1]`
    :param enemy_hp: Health points of the enemy

    :return: Average number of deads in the enemy squad.
    """
    return round(enemy_dead + ((enemy_hp - remaining_hp)/enemy_hp), 2)

def compute_average_hp_lost(enemy_dead: float, remaining_hp: float, enemy_hp: int) -> float:
    """
    Compute the average number of HP lost after an attack (useful for monsters or vehicule).

    In our computation, we have:
    * enemy_dead: average nb of dead figurine after an attack
    * remaining_hp: number of HP remaining of the figurine not dead

    :param enemy_dead: Result from `src.workflow.launch_workflow[0]`
    :param remaining_hp: Result from `src.workflow.launch_workflow[1]`
    :param enemy_hp: Health points of the enemy

    :return: Average number of deads in the enemy squad.
    :return: Average number of HP lost in the enemy squad.
    """
    return round(enemy_dead*enemy_hp + (enemy_hp-remaining_hp), 2)

if __name__ == "__main__":
    parse_expression("2D6") # DiceExpression(nb_dice=2, dice_face=6, bonus=0)
    parse_expression("1D3+9")  # DiceExpression(nb_dice=1, dice_face=3, bonus=9)
