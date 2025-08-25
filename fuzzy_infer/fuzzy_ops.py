"""
Fuzzy set operations and membership functions.

This module provides various fuzzy set operations and membership functions
for use in fuzzy logic systems.
"""

import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

# Fuzzy Set Operations (T-norms and T-conorms)


def fuzzy_and_min(a: float, b: float) -> float:
    """
    Fuzzy AND using minimum (Zadeh's AND).

    This is the standard fuzzy AND operation.

    Args:
        a: First membership degree [0, 1]
        b: Second membership degree [0, 1]

    Returns:
        min(a, b)
    """
    return min(a, b)


def fuzzy_and_product(a: float, b: float) -> float:
    """
    Fuzzy AND using algebraic product.

    Args:
        a: First membership degree [0, 1]
        b: Second membership degree [0, 1]

    Returns:
        a * b
    """
    return a * b


def fuzzy_and_lukasiewicz(a: float, b: float) -> float:
    """
    Fuzzy AND using Łukasiewicz t-norm.

    Args:
        a: First membership degree [0, 1]
        b: Second membership degree [0, 1]

    Returns:
        max(0, a + b - 1)
    """
    return max(0.0, a + b - 1.0)


def fuzzy_or_max(a: float, b: float) -> float:
    """
    Fuzzy OR using maximum (Zadeh's OR).

    This is the standard fuzzy OR operation.

    Args:
        a: First membership degree [0, 1]
        b: Second membership degree [0, 1]

    Returns:
        max(a, b)
    """
    return max(a, b)


def fuzzy_or_probabilistic(a: float, b: float) -> float:
    """
    Fuzzy OR using probabilistic sum.

    Args:
        a: First membership degree [0, 1]
        b: Second membership degree [0, 1]

    Returns:
        a + b - a * b
    """
    return a + b - a * b


def fuzzy_or_lukasiewicz(a: float, b: float) -> float:
    """
    Fuzzy OR using Łukasiewicz t-conorm.

    Args:
        a: First membership degree [0, 1]
        b: Second membership degree [0, 1]

    Returns:
        min(1, a + b)
    """
    return min(1.0, a + b)


def fuzzy_not(a: float) -> float:
    """
    Fuzzy NOT (complement).

    Args:
        a: Membership degree [0, 1]

    Returns:
        1 - a
    """
    return 1.0 - a


def fuzzy_implication_lukasiewicz(a: float, b: float) -> float:
    """
    Fuzzy implication using Łukasiewicz implication.

    Args:
        a: Antecedent membership degree [0, 1]
        b: Consequent membership degree [0, 1]

    Returns:
        min(1, 1 - a + b)
    """
    return min(1.0, 1.0 - a + b)


def fuzzy_implication_godel(a: float, b: float) -> float:
    """
    Fuzzy implication using Gödel implication.

    Args:
        a: Antecedent membership degree [0, 1]
        b: Consequent membership degree [0, 1]

    Returns:
        1 if a <= b else b
    """
    return 1.0 if a <= b else b


# Membership Functions


@dataclass
class MembershipFunction:
    """Base class for membership functions."""

    def __call__(self, x: float) -> float:
        """Evaluate the membership function at x."""
        raise NotImplementedError


@dataclass
class TriangularMF(MembershipFunction):
    """
    Triangular membership function.

    Attributes:
        a: Left foot (start of triangle)
        b: Peak (center of triangle)
        c: Right foot (end of triangle)
    """

    a: float
    b: float
    c: float

    def __call__(self, x: float) -> float:
        """
        Evaluate triangular membership function.

        Args:
            x: Input value

        Returns:
            Membership degree [0, 1]
        """
        if x <= self.a or x >= self.c:
            return 0.0
        elif x == self.b:
            return 1.0
        elif x < self.b:
            return (x - self.a) / (self.b - self.a)
        else:
            return (self.c - x) / (self.c - self.b)


@dataclass
class TrapezoidalMF(MembershipFunction):
    """
    Trapezoidal membership function.

    Attributes:
        a: Left foot
        b: Left shoulder
        c: Right shoulder
        d: Right foot
    """

    a: float
    b: float
    c: float
    d: float

    def __call__(self, x: float) -> float:
        """
        Evaluate trapezoidal membership function.

        Args:
            x: Input value

        Returns:
            Membership degree [0, 1]
        """
        if x <= self.a or x >= self.d:
            return 0.0
        elif self.b <= x <= self.c:
            return 1.0
        elif x < self.b:
            return (x - self.a) / (self.b - self.a)
        else:
            return (self.d - x) / (self.d - self.c)


@dataclass
class GaussianMF(MembershipFunction):
    """
    Gaussian membership function.

    Attributes:
        center: Center of the Gaussian
        sigma: Standard deviation
    """

    center: float
    sigma: float

    def __call__(self, x: float) -> float:
        """
        Evaluate Gaussian membership function.

        Args:
            x: Input value

        Returns:
            Membership degree [0, 1]
        """
        return math.exp(-0.5 * ((x - self.center) / self.sigma) ** 2)


@dataclass
class SigmoidMF(MembershipFunction):
    """
    Sigmoid membership function.

    Attributes:
        a: Slope parameter
        c: Inflection point
    """

    a: float
    c: float

    def __call__(self, x: float) -> float:
        """
        Evaluate sigmoid membership function.

        Args:
            x: Input value

        Returns:
            Membership degree [0, 1]
        """
        return 1.0 / (1.0 + math.exp(-self.a * (x - self.c)))


@dataclass
class BellMF(MembershipFunction):
    """
    Generalized bell membership function.

    Attributes:
        a: Width parameter
        b: Shape parameter
        c: Center
    """

    a: float
    b: float
    c: float

    def __call__(self, x: float) -> float:
        """
        Evaluate bell membership function.

        Args:
            x: Input value

        Returns:
            Membership degree [0, 1]
        """
        return 1.0 / (1.0 + abs((x - self.c) / self.a) ** (2 * self.b))


# Fuzzy Set Class


@dataclass
class FuzzySet:
    """
    Represents a fuzzy set with a membership function.

    Attributes:
        name: Name of the fuzzy set
        membership_fn: Membership function
        universe: Optional universe of discourse (min, max)
    """

    name: str
    membership_fn: MembershipFunction
    universe: Optional[Tuple[float, float]] = None

    def membership(self, x: float) -> float:
        """
        Get membership degree for a value.

        Args:
            x: Input value

        Returns:
            Membership degree [0, 1]
        """
        if self.universe:
            min_val, max_val = self.universe
            if x < min_val or x > max_val:
                return 0.0
        return self.membership_fn(x)

    def union(self, other: "FuzzySet", t_conorm: Callable = fuzzy_or_max) -> Callable:
        """
        Create union with another fuzzy set.

        Args:
            other: Other fuzzy set
            t_conorm: T-conorm operation to use

        Returns:
            Function that computes union membership
        """

        def union_membership(x: float) -> float:
            return t_conorm(self.membership(x), other.membership(x))

        return union_membership

    def intersection(self, other: "FuzzySet", t_norm: Callable = fuzzy_and_min) -> Callable:
        """
        Create intersection with another fuzzy set.

        Args:
            other: Other fuzzy set
            t_norm: T-norm operation to use

        Returns:
            Function that computes intersection membership
        """

        def intersection_membership(x: float) -> float:
            return t_norm(self.membership(x), other.membership(x))

        return intersection_membership

    def complement(self) -> Callable:
        """
        Create complement of the fuzzy set.

        Returns:
            Function that computes complement membership
        """

        def complement_membership(x: float) -> float:
            return fuzzy_not(self.membership(x))

        return complement_membership

    def alpha_cut(self, alpha: float) -> Callable:
        """
        Create alpha-cut of the fuzzy set.

        Args:
            alpha: Threshold value [0, 1]

        Returns:
            Function that returns 1 if membership >= alpha, 0 otherwise
        """

        def alpha_cut_membership(x: float) -> float:
            return 1.0 if self.membership(x) >= alpha else 0.0

        return alpha_cut_membership


# Defuzzification Methods


def defuzzify_centroid(values: List[Tuple[float, float]]) -> float:
    """
    Defuzzify using centroid method (center of gravity).

    Args:
        values: List of (value, membership) pairs

    Returns:
        Defuzzified crisp value
    """
    if not values:
        return 0.0

    numerator = sum(x * mu for x, mu in values)
    denominator = sum(mu for _, mu in values)

    if denominator == 0:
        return 0.0

    return numerator / denominator


def defuzzify_bisector(values: List[Tuple[float, float]]) -> float:
    """
    Defuzzify using bisector method.

    Args:
        values: List of (value, membership) pairs

    Returns:
        Defuzzified crisp value
    """
    if not values:
        return 0.0

    sorted_values = sorted(values, key=lambda x: x[0])
    total_area = sum(mu for _, mu in sorted_values)
    half_area = total_area / 2.0

    accumulated = 0.0
    for x, mu in sorted_values:
        accumulated += mu
        if accumulated >= half_area:
            return x

    return sorted_values[-1][0] if sorted_values else 0.0


def defuzzify_mom(values: List[Tuple[float, float]]) -> float:
    """
    Defuzzify using mean of maximum method.

    Args:
        values: List of (value, membership) pairs

    Returns:
        Defuzzified crisp value
    """
    if not values:
        return 0.0

    max_membership = max(mu for _, mu in values)
    max_values = [x for x, mu in values if mu == max_membership]

    return sum(max_values) / len(max_values) if max_values else 0.0


def defuzzify_som(values: List[Tuple[float, float]]) -> float:
    """
    Defuzzify using smallest of maximum method.

    Args:
        values: List of (value, membership) pairs

    Returns:
        Defuzzified crisp value
    """
    if not values:
        return 0.0

    max_membership = max(mu for _, mu in values)
    max_values = [x for x, mu in values if mu == max_membership]

    return min(max_values) if max_values else 0.0


def defuzzify_lom(values: List[Tuple[float, float]]) -> float:
    """
    Defuzzify using largest of maximum method.

    Args:
        values: List of (value, membership) pairs

    Returns:
        Defuzzified crisp value
    """
    if not values:
        return 0.0

    max_membership = max(mu for _, mu in values)
    max_values = [x for x, mu in values if mu == max_membership]

    return max(max_values) if max_values else 0.0


# Fuzzy Relations


class FuzzyRelation:
    """
    Represents a fuzzy relation between two sets.
    """

    def __init__(self, membership_matrix: List[List[float]]):
        """
        Initialize fuzzy relation.

        Args:
            membership_matrix: 2D matrix of membership degrees
        """
        self.matrix = membership_matrix
        self.rows = len(membership_matrix)
        self.cols = len(membership_matrix[0]) if membership_matrix else 0

    def compose(
        self,
        other: "FuzzyRelation",
        t_norm: Callable = fuzzy_and_min,
        t_conorm: Callable = fuzzy_or_max,
    ) -> "FuzzyRelation":
        """
        Compose with another fuzzy relation (max-min composition by default).

        Args:
            other: Other fuzzy relation
            t_norm: T-norm for composition
            t_conorm: T-conorm for composition

        Returns:
            Composed fuzzy relation
        """
        if self.cols != other.rows:
            raise ValueError("Incompatible dimensions for composition")

        result = []
        for i in range(self.rows):
            row = []
            for j in range(other.cols):
                values = [t_norm(self.matrix[i][k], other.matrix[k][j]) for k in range(self.cols)]
                row.append(max(values) if values else 0.0)
            result.append(row)

        return FuzzyRelation(result)
