"""Interpolation linéaire exacte, partagée par la table XP (T5) et la calibration (T7).

Module neutre : ni source ni règle, pour que `rules/` n'importe jamais `sources/`.
"""

from bisect import bisect_right
from fractions import Fraction


def interpolate(points, value):
    """Interpole linéairement, sans arrondi ni extrapolation.

    Args:
        points: tuple de couples (x, y) entiers, x strictement croissant.
        value: nombre fini, `int`, `float` ou `Fraction`.

    Returns:
        Le `Fraction` exact de y en `value`, ou `None` hors de l'intervalle des x.
    """
    if not points[0][0] <= value <= points[-1][0]:
        return None
    index = bisect_right([x for x, _ in points], value) - 1
    if index == len(points) - 1:
        return Fraction(points[-1][1])
    (x0, y0), (x1, y1) = points[index], points[index + 1]
    return y0 + (Fraction(value) - x0) * Fraction(y1 - y0, x1 - x0)
