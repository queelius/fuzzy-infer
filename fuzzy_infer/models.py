"""
Data models for the FuzzyInfer system.

This module provides dataclasses for Facts, Rules, Conditions, and Actions
with validation and pythonic interfaces.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from fuzzy_infer.exceptions import FactValidationError, RuleValidationError


@dataclass
class Fact:
    """
    Represents a fuzzy fact in the knowledge base.

    Attributes:
        predicate: The predicate name (e.g., 'is-zebra')
        args: List of arguments for the predicate
        degree: Degree of membership (0.0 to 1.0)

    Examples:
        >>> fact = Fact('is-zebra', ['sam'], 0.8)
        >>> fact.predicate
        'is-zebra'
        >>> fact.degree
        0.8
    """

    predicate: str
    args: List[Union[str, Any]]
    degree: float = 1.0

    def __post_init__(self):
        """Validate the fact after initialization."""
        if not self.predicate:
            raise FactValidationError("Predicate cannot be empty")
        if not isinstance(self.args, list):
            raise FactValidationError("Arguments must be a list")
        if not 0.0 <= self.degree <= 1.0:
            raise FactValidationError(f"Degree must be between 0 and 1, got {self.degree}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert fact to dictionary representation."""
        return {"pred": self.predicate, "args": self.args, "deg": self.degree}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fact":
        """Create a Fact from dictionary representation."""
        return cls(
            predicate=data.get("pred", data.get("predicate", "")),
            args=data.get("args", []),
            degree=data.get("deg", data.get("degree", 1.0)),
        )

    def matches_pattern(
        self, pattern: "Fact", bindings: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if this fact matches a pattern with variables.

        Args:
            pattern: Pattern fact potentially containing variables (e.g., '?x')
            bindings: Existing variable bindings

        Returns:
            Tuple of (matches: bool, updated_bindings: dict)
        """
        if bindings is None:
            bindings = {}

        if self.predicate != pattern.predicate:
            return False, bindings

        if len(self.args) != len(pattern.args):
            return False, bindings

        new_bindings = bindings.copy()
        for self_arg, pattern_arg in zip(self.args, pattern.args):
            if isinstance(pattern_arg, str) and pattern_arg.startswith("?"):
                # Variable binding
                if pattern_arg in new_bindings:
                    if new_bindings[pattern_arg] != self_arg:
                        return False, bindings
                else:
                    new_bindings[pattern_arg] = self_arg
            elif self_arg != pattern_arg:
                return False, bindings

        return True, new_bindings

    def __hash__(self):
        """Make Fact hashable for use in sets."""
        return hash((self.predicate, tuple(self.args), self.degree))

    def __eq__(self, other):
        """Check equality based on predicate and arguments (not degree)."""
        if not isinstance(other, Fact):
            return False
        return self.predicate == other.predicate and self.args == other.args


@dataclass
class Condition:
    """
    Represents a condition in a rule.

    Attributes:
        predicate: The predicate to match
        args: Arguments (can contain variables like '?x')
        degree_var: Variable to bind the degree to
        degree_constraint: Optional constraint on degree (e.g., ['>', '?d', 0.5])
        negated: Whether this is a negated condition
        or_conditions: List of OR'ed conditions
        and_conditions: List of AND'ed conditions
    """

    predicate: Optional[str] = None
    args: List[Union[str, Any]] = field(default_factory=list)
    degree_var: Optional[str] = None
    degree_constraint: Optional[List[Any]] = None
    negated: bool = False
    or_conditions: Optional[List["Condition"]] = None
    and_conditions: Optional[List["Condition"]] = None

    def __post_init__(self):
        """Validate the condition."""
        if not any([self.predicate, self.or_conditions, self.and_conditions]):
            raise RuleValidationError("Condition must have a predicate or logical operators")

    def to_dict(self) -> Dict[str, Any]:
        """Convert condition to dictionary representation."""
        if self.or_conditions:
            return {"or": [c.to_dict() for c in self.or_conditions]}
        if self.and_conditions:
            return {"and": [c.to_dict() for c in self.and_conditions]}

        result = {"pred": self.predicate, "args": self.args}
        if self.degree_var:
            result["deg"] = self.degree_var
        if self.degree_constraint:
            result["deg-pred"] = self.degree_constraint
        if self.negated:
            return {"not": result}
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Condition":
        """Create a Condition from dictionary representation."""
        if "or" in data:
            return cls(or_conditions=[cls.from_dict(c) for c in data["or"]])
        if "and" in data:
            return cls(and_conditions=[cls.from_dict(c) for c in data["and"]])
        if "not" in data:
            inner = data["not"]
            return cls(
                predicate=inner.get("pred"),
                args=inner.get("args", []),
                degree_var=inner.get("deg"),
                degree_constraint=inner.get("deg-pred"),
                negated=True,
            )

        return cls(
            predicate=data.get("pred"),
            args=data.get("args", []),
            degree_var=data.get("deg"),
            degree_constraint=data.get("deg-pred"),
        )


@dataclass
class Action:
    """
    Represents an action to take when a rule fires.

    Attributes:
        action_type: Type of action ('add', 'remove', 'modify')
        fact: Fact to add/remove/modify
    """

    action_type: str
    fact: Dict[str, Any]

    def __post_init__(self):
        """Validate the action."""
        if self.action_type not in ["add", "remove", "modify"]:
            raise RuleValidationError(f"Invalid action type: {self.action_type}")
        if not self.fact:
            raise RuleValidationError("Action must specify a fact")

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary representation."""
        return {"action": self.action_type, "fact": self.fact}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """Create an Action from dictionary representation."""
        return cls(action_type=data.get("action", "add"), fact=data.get("fact", {}))


@dataclass
class Rule:
    """
    Represents a production rule with conditions and actions.

    Attributes:
        conditions: List of conditions that must be satisfied
        actions: List of actions to execute when conditions are met
        name: Optional name for the rule
        priority: Priority for rule execution (higher = earlier)
    """

    conditions: List[Condition]
    actions: List[Action]
    name: Optional[str] = None
    priority: int = 0

    def __post_init__(self):
        """Validate the rule."""
        if not self.conditions:
            raise RuleValidationError("Rule must have at least one condition")
        if not self.actions:
            raise RuleValidationError("Rule must have at least one action")

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary representation."""
        result = {
            "cond": [c.to_dict() for c in self.conditions],
            "actions": [a.to_dict() for a in self.actions],
        }
        if self.name:
            result["name"] = self.name
        if self.priority != 0:
            result["priority"] = self.priority
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Rule":
        """Create a Rule from dictionary representation."""
        conditions = []
        raw_conditions = data.get("cond", data.get("conditions", []))
        for cond in raw_conditions:
            conditions.append(Condition.from_dict(cond))

        actions = []
        raw_actions = data.get("actions", [])
        for action in raw_actions:
            actions.append(Action.from_dict(action))

        return cls(
            conditions=conditions,
            actions=actions,
            name=data.get("name"),
            priority=data.get("priority", 0),
        )


class RuleBuilder:
    """
    Builder pattern for constructing complex rules.

    Example:
        >>> rule = (RuleBuilder()
        ...     .when('is-zebra', ['?x'])
        ...     .with_degree_greater_than(0.5)
        ...     .then_add('has-stripes', ['?x'])
        ...     .with_degree_multiplied_by(0.9)
        ...     .build())
    """

    def __init__(self):
        """Initialize the builder."""
        self.conditions = []
        self.actions = []
        self.current_condition = None
        self.current_action = None
        self.name = None
        self.priority = 0
        self.degree_var = None  # Track degree variable

    def when(self, predicate: str, args: List[Union[str, Any]]) -> "RuleBuilder":
        """Add a condition to the rule."""
        self.current_condition = Condition(predicate=predicate, args=args)
        self.conditions.append(self.current_condition)
        return self

    def when_not(self, predicate: str, args: List[Union[str, Any]]) -> "RuleBuilder":
        """Add a negated condition to the rule."""
        self.current_condition = Condition(predicate=predicate, args=args, negated=True)
        self.conditions.append(self.current_condition)
        return self

    def with_degree_greater_than(self, threshold: float, var_name: str = "?d") -> "RuleBuilder":
        """Add a degree constraint to the current condition."""
        if not self.current_condition:
            raise RuleValidationError("No condition to add degree constraint to")
        self.current_condition.degree_var = var_name
        self.current_condition.degree_constraint = [">", var_name, threshold]
        self.degree_var = var_name  # Store for later use
        return self

    def with_degree_less_than(self, threshold: float, var_name: str = "?d") -> "RuleBuilder":
        """Add a degree constraint to the current condition."""
        if not self.current_condition:
            raise RuleValidationError("No condition to add degree constraint to")
        self.current_condition.degree_var = var_name  
        self.current_condition.degree_constraint = ["<", var_name, threshold]
        self.degree_var = var_name  # Store for later use
        return self

    def then_add(
        self, predicate: str, args: List[Union[str, Any]], degree: float = 1.0
    ) -> "RuleBuilder":
        """Add an action to add a fact."""
        fact = {"pred": predicate, "args": args, "deg": degree}
        self.current_action = Action(action_type="add", fact=fact)
        self.actions.append(self.current_action)
        return self

    def then_remove(self, predicate: str, args: List[Union[str, Any]]) -> "RuleBuilder":
        """Add an action to remove a fact."""
        fact = {"pred": predicate, "args": args}
        self.current_action = Action(action_type="remove", fact=fact)
        self.actions.append(self.current_action)
        return self

    def with_degree_multiplied_by(self, factor: float) -> "RuleBuilder":
        """Modify the degree of the current action's fact."""
        if not self.current_action or self.current_action.action_type != "add":
            raise RuleValidationError("No add action to modify degree for")
        # Always create a degree variable for the first condition if none exists
        if not hasattr(self, 'degree_var') or self.degree_var is None:
            # Add degree variable to first condition
            if self.conditions:
                self.conditions[0].degree_var = "?_deg"
                self.degree_var = "?_deg"
        
        # Use the degree variable to multiply
        if self.degree_var:
            self.current_action.fact["deg"] = ["*", factor, self.degree_var]
        else:
            # Fallback to just using the factor
            self.current_action.fact["deg"] = factor
        return self

    def named(self, name: str) -> "RuleBuilder":
        """Set the rule's name."""
        self.name = name
        return self

    def with_priority(self, priority: int) -> "RuleBuilder":
        """Set the rule's priority."""
        self.priority = priority
        return self

    def build(self) -> Rule:
        """Build and return the Rule object."""
        return Rule(
            conditions=self.conditions, actions=self.actions, name=self.name, priority=self.priority
        )
