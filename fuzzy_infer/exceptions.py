"""
Custom exceptions for the FuzzyInfer package.

This module defines all custom exceptions used throughout the FuzzyInfer system
for better error handling and debugging.
"""


class FuzzyInferError(Exception):
    """Base exception for all FuzzyInfer errors."""

    pass


class FactValidationError(FuzzyInferError):
    """Raised when a fact fails validation."""

    pass


class RuleValidationError(FuzzyInferError):
    """Raised when a rule fails validation."""

    pass


class InferenceError(FuzzyInferError):
    """Raised when an error occurs during inference."""

    pass


class DegreeCalculationError(FuzzyInferError):
    """Raised when degree calculation fails."""

    pass


class CyclicRuleError(FuzzyInferError):
    """Raised when cyclic dependencies are detected in rules."""

    pass


class QueryError(FuzzyInferError):
    """Raised when a query cannot be processed."""

    pass
