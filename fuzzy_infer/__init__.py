"""
FuzzyInfer: A Fuzzy Forward-Chaining Production Rule System

A Python-based production rule system designed for fuzzy inference,
extending classical forward-chaining systems by incorporating fuzzy logic
for handling uncertainty and degrees of belief.
"""

from fuzzy_infer.core import FuzzyInfer
from fuzzy_infer.exceptions import (
    FactValidationError,
    FuzzyInferError,
    InferenceError,
    RuleValidationError,
)
from fuzzy_infer.models import Action, Condition, Fact, Rule, RuleBuilder

__version__ = "0.1.0"
__author__ = "FuzzyInfer Contributors"
__license__ = "MIT"

__all__ = [
    "Action",
    "Condition",
    "Fact",
    "FactValidationError",
    "FuzzyInfer",
    "FuzzyInferError",
    "InferenceError",
    "Rule",
    "RuleBuilder",
    "RuleValidationError",
]
