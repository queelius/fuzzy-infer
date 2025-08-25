"""
Core inference engine for the FuzzyInfer system.

This module contains the main FuzzyInfer class that implements
forward-chaining fuzzy inference with proper type hints and modern Python patterns.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from fuzzy_infer.exceptions import (
    DegreeCalculationError,
    InferenceError,
)
from fuzzy_infer.models import Action, Condition, Fact, Rule

logger = logging.getLogger(__name__)


class FuzzyInfer:
    """
    Production rule system for fuzzy inference.

    This class implements a forward-chaining inference engine with fuzzy logic
    support, allowing for reasoning with uncertain information and degrees of belief.

    Attributes:
        facts: Set of facts in the knowledge base
        rules: List of production rules
        inference_log: Log of inference steps for debugging
        max_iterations: Maximum iterations for inference loop

    Examples:
        >>> # Basic usage
        >>> inf = FuzzyInfer()
        >>> inf.add_fact(Fact('is-zebra', ['sam'], 0.8))
        >>> inf.add_rule(RuleBuilder()
        ...     .when('is-zebra', ['?x'])
        ...     .with_degree_greater_than(0.5)
        ...     .then_add('has-stripes', ['?x'])
        ...     .with_degree_multiplied_by(0.9)
        ...     .build())
        >>> inf.run()
        >>> results = inf.query('has-stripes', ['sam'])

        >>> # Fluent API
        >>> inf = (FuzzyInfer()
        ...     .add_fact(Fact('is-person', ['alice'], 1.0))
        ...     .add_fact(Fact('is-tall', ['alice'], 0.7))
        ...     .add_rule(tall_person_rule)
        ...     .run())

        >>> # Context manager
        >>> with FuzzyInfer.session() as inf:
        ...     inf.add_facts(facts)
        ...     inf.add_rules(rules)
        ...     inf.run()
        ...     results = inf.query('target-pred', ['arg'])
    """

    def __init__(self, max_iterations: int = 100):
        """
        Initialize the FuzzyInfer inference engine.

        Args:
            max_iterations: Maximum number of inference iterations
        """
        self.facts: Dict[Tuple[str, Tuple], Fact] = {}
        self.rules: List[Rule] = []
        self.inference_log: List[str] = []
        self.max_iterations = max_iterations
        self._iteration_count = 0
        self._rule_history: Set[Tuple] = set()

    @classmethod
    @contextmanager
    def session(cls, **kwargs):
        """
        Create a FuzzyInfer session as a context manager.

        Yields:
            FuzzyInfer: Configured inference engine

        Examples:
            >>> with FuzzyInfer.session(max_iterations=50) as inf:
            ...     inf.add_facts(facts)
            ...     results = inf.run()
        """
        engine = cls(**kwargs)
        try:
            yield engine
        finally:
            logger.info(f"Inference session completed with {len(engine.facts)} facts")

    def add_fact(self, fact: Union[Fact, Dict[str, Any]]) -> "FuzzyInfer":
        """
        Add a single fact to the knowledge base.

        Args:
            fact: Fact object or dictionary representation

        Returns:
            Self for method chaining

        Examples:
            >>> inf.add_fact(Fact('is-person', ['sam'], 1.0))
            >>> inf.add_fact({'pred': 'is-tall', 'args': ['sam'], 'deg': 0.8})
        """
        if isinstance(fact, dict):
            fact = Fact.from_dict(fact)

        key = (fact.predicate, tuple(fact.args))

        # Fuzzy OR: take maximum degree if fact already exists
        if key in self.facts:
            existing_fact = self.facts[key]
            if fact.degree > existing_fact.degree:
                self.facts[key] = fact
                logger.debug(f"Updated fact {key} degree: {existing_fact.degree} -> {fact.degree}")
        else:
            self.facts[key] = fact
            logger.debug(f"Added fact: {fact.predicate}{fact.args} [deg={fact.degree}]")

        return self

    def add_facts(self, facts: List[Union[Fact, Dict[str, Any]]]) -> "FuzzyInfer":
        """
        Add multiple facts to the knowledge base.

        Args:
            facts: List of Fact objects or dictionary representations

        Returns:
            Self for method chaining
        """
        for fact in facts:
            self.add_fact(fact)
        return self

    def add_rule(self, rule: Union[Rule, Dict[str, Any]]) -> "FuzzyInfer":
        """
        Add a single rule to the rule base.

        Args:
            rule: Rule object or dictionary representation

        Returns:
            Self for method chaining
        """
        if isinstance(rule, dict):
            rule = Rule.from_dict(rule)

        self.rules.append(rule)
        # Sort rules by priority (higher first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.debug(f"Added rule: {rule.name or f'Rule#{len(self.rules)}'}")

        return self

    def add_rules(self, rules: List[Union[Rule, Dict[str, Any]]]) -> "FuzzyInfer":
        """
        Add multiple rules to the rule base.

        Args:
            rules: List of Rule objects or dictionary representations

        Returns:
            Self for method chaining
        """
        for rule in rules:
            self.add_rule(rule)
        return self

    def _evaluate_degree_constraint(self, constraint: List[Any], bindings: Dict[str, Any]) -> bool:
        """
        Evaluate a degree constraint expression.

        Args:
            constraint: Constraint expression ['>', '?d', 0.5]
            bindings: Variable bindings

        Returns:
            True if constraint is satisfied
        """
        if not constraint or len(constraint) < 3:
            return True

        op, var, threshold = constraint[0], constraint[1], constraint[2]

        # Resolve variable
        if isinstance(var, str) and var.startswith("?"):
            if var not in bindings:
                return False
            value = bindings[var]
        else:
            value = var

        # Evaluate constraint
        if op == ">":
            return value > threshold
        elif op == "<":
            return value < threshold
        elif op == ">=":
            return value >= threshold
        elif op == "<=":
            return value <= threshold
        elif op == "==":
            return value == threshold
        elif op == "!=":
            return value != threshold
        else:
            raise DegreeCalculationError(f"Unknown operator: {op}")

    def _calculate_degree(
        self, degree_expr: Union[float, List[Any]], bindings: Dict[str, Any]
    ) -> float:
        """
        Calculate a degree value from an expression.

        Args:
            degree_expr: Degree expression (float or ['*', 0.9, '?d'])
            bindings: Variable bindings

        Returns:
            Calculated degree value
        """
        if isinstance(degree_expr, (int, float)):
            return float(degree_expr)

        if not isinstance(degree_expr, list) or len(degree_expr) < 3:
            return 1.0

        op = degree_expr[0]
        operands = []

        for operand in degree_expr[1:]:
            if isinstance(operand, str) and operand.startswith("?"):
                if operand not in bindings:
                    raise DegreeCalculationError(f"Unbound variable: {operand}")
                operands.append(bindings[operand])
            else:
                operands.append(operand)

        if op == "*":
            result = operands[0]
            for val in operands[1:]:
                result *= val
        elif op == "+":
            result = sum(operands)
        elif op == "-":
            result = operands[0] - sum(operands[1:])
        elif op == "/":
            result = operands[0] / operands[1] if operands[1] != 0 else 0
        elif op == "min":
            result = min(operands)
        elif op == "max":
            result = max(operands)
        else:
            raise DegreeCalculationError(f"Unknown operation: {op}")

        # Clamp to [0, 1]
        return max(0.0, min(1.0, result))

    def _match_condition(
        self, condition: Condition, bindings: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], float]:
        """
        Check if a condition matches the current facts.

        Args:
            condition: Condition to match
            bindings: Current variable bindings

        Returns:
            Tuple of (matches, updated_bindings, degree)
        """
        # Handle logical operators
        if condition.or_conditions:
            for or_cond in condition.or_conditions:
                matched, new_bindings, degree = self._match_condition(or_cond, bindings)
                if matched:
                    return True, new_bindings, degree
            return False, bindings, 0.0

        if condition.and_conditions:
            combined_bindings = bindings.copy()
            min_degree = 1.0
            for and_cond in condition.and_conditions:
                matched, combined_bindings, degree = self._match_condition(
                    and_cond, combined_bindings
                )
                if not matched:
                    return False, bindings, 0.0
                min_degree = min(min_degree, degree)
            return True, combined_bindings, min_degree

        # Handle negation
        if condition.negated:
            # Create a non-negated version
            temp_cond = Condition(
                predicate=condition.predicate,
                args=condition.args,
                degree_var=condition.degree_var,
                degree_constraint=condition.degree_constraint,
            )
            matched, _, _ = self._match_condition(temp_cond, bindings)
            return not matched, bindings, 1.0 if not matched else 0.0

        # Match against facts
        pattern_fact = Fact(condition.predicate, condition.args, 1.0)

        for fact_key, fact in self.facts.items():
            matched, new_bindings = fact.matches_pattern(pattern_fact, bindings)
            if matched:
                # Check degree constraint
                if condition.degree_var:
                    new_bindings[condition.degree_var] = fact.degree

                if condition.degree_constraint:
                    if not self._evaluate_degree_constraint(
                        condition.degree_constraint, new_bindings
                    ):
                        continue

                return True, new_bindings, fact.degree

        return False, bindings, 0.0
    
    def _match_all_conditions(
        self, condition: Condition, bindings: Dict[str, Any]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find ALL facts that match a condition, not just the first one.

        Args:
            condition: Condition to match
            bindings: Current variable bindings

        Returns:
            List of tuples (updated_bindings, degree) for all matches
        """
        all_matches = []
        
        # Handle logical operators
        if condition.or_conditions:
            for or_cond in condition.or_conditions:
                matches = self._match_all_conditions(or_cond, bindings)
                all_matches.extend(matches)
            return all_matches

        if condition.and_conditions:
            # For AND, we need all conditions to match
            current_matches = [(bindings.copy(), 1.0)]
            for and_cond in condition.and_conditions:
                new_matches = []
                for curr_bindings, curr_degree in current_matches:
                    cond_matches = self._match_all_conditions(and_cond, curr_bindings)
                    for new_bind, new_deg in cond_matches:
                        new_matches.append((new_bind, min(curr_degree, new_deg)))
                current_matches = new_matches
                if not current_matches:
                    return []
            return current_matches

        # Handle negation
        if condition.negated:
            # Create a non-negated version
            temp_cond = Condition(
                predicate=condition.predicate,
                args=condition.args,
                degree_var=condition.degree_var,
                degree_constraint=condition.degree_constraint,
            )
            matches = self._match_all_conditions(temp_cond, bindings)
            if not matches:
                return [(bindings, 1.0)]
            return []

        # Match against ALL facts
        pattern_fact = Fact(condition.predicate, condition.args, 1.0)

        for fact_key, fact in self.facts.items():
            matched, new_bindings = fact.matches_pattern(pattern_fact, bindings)
            if matched:
                # Check degree constraint
                if condition.degree_var:
                    new_bindings[condition.degree_var] = fact.degree

                if condition.degree_constraint:
                    if not self._evaluate_degree_constraint(
                        condition.degree_constraint, new_bindings
                    ):
                        continue

                all_matches.append((new_bindings, fact.degree))

        return all_matches

    def _satisfies_conditions(self, conditions: List[Condition]) -> List[Dict[str, Any]]:
        """
        Check if conditions are satisfied and return all possible bindings.

        Args:
            conditions: List of conditions to check

        Returns:
            List of all possible variable bindings that satisfy conditions
        """
        if not conditions:
            return [{}]

        all_bindings = [{}]

        for condition in conditions:
            new_all_bindings = []
            for bindings in all_bindings:
                # Use _match_all_conditions to get ALL matching facts
                matches = self._match_all_conditions(condition, bindings)
                for new_bind, degree in matches:
                    new_all_bindings.append(new_bind)
            all_bindings = new_all_bindings

            if not all_bindings:
                return []

        return all_bindings

    def _apply_action(self, action: Action, bindings: Dict[str, Any]) -> None:
        """
        Apply an action with the given variable bindings.

        Args:
            action: Action to apply
            bindings: Variable bindings
        """
        fact_dict = action.fact.copy()

        # Substitute variables in arguments
        if "args" in fact_dict:
            new_args = []
            for arg in fact_dict["args"]:
                if isinstance(arg, str) and arg.startswith("?"):
                    if arg in bindings:
                        new_args.append(bindings[arg])
                    else:
                        logger.warning(f"Unbound variable in action: {arg}")
                        return
                else:
                    new_args.append(arg)
            fact_dict["args"] = new_args

        # Calculate degree
        if "deg" in fact_dict:
            fact_dict["deg"] = self._calculate_degree(fact_dict["deg"], bindings)

        # Apply action
        if action.action_type == "add":
            new_fact = Fact.from_dict(fact_dict)
            self.add_fact(new_fact)
        elif action.action_type == "remove":
            key = (fact_dict.get("pred"), tuple(fact_dict.get("args", [])))
            if key in self.facts:
                del self.facts[key]
                logger.debug(f"Removed fact: {key}")
        elif action.action_type == "modify":
            key = (fact_dict.get("pred"), tuple(fact_dict.get("args", [])))
            if key in self.facts:
                self.facts[key].degree = fact_dict.get("deg", 1.0)
                logger.debug(f"Modified fact degree: {key} -> {self.facts[key].degree}")

    def run(self) -> "FuzzyInfer":
        """
        Execute the forward-chaining inference process.

        Returns:
            Self for method chaining

        Raises:
            InferenceError: If maximum iterations exceeded
        """
        self._iteration_count = 0
        facts_before = len(self.facts)

        while self._iteration_count < self.max_iterations:
            self._iteration_count += 1
            changed = False

            for rule in self.rules:
                # Check if conditions are satisfied
                all_bindings = self._satisfies_conditions(rule.conditions)

                for bindings in all_bindings:
                    # Create a unique key for this rule application
                    rule_key = (id(rule), tuple(sorted(bindings.items())))

                    # Skip if we've already applied this exact rule with these bindings
                    if rule_key in self._rule_history:
                        continue

                    self._rule_history.add(rule_key)

                    # Apply actions
                    for action in rule.actions:
                        self._apply_action(action, bindings)

                    changed = True

                    if rule.name:
                        logger.info(f"Fired rule: {rule.name} with bindings {bindings}")

            if not changed:
                break

        if self._iteration_count >= self.max_iterations:
            raise InferenceError(
                f"Inference did not converge after {self.max_iterations} iterations"
            )

        facts_after = len(self.facts)
        logger.info(
            f"Inference completed in {self._iteration_count} iterations. "
            f"Facts: {facts_before} -> {facts_after}"
        )

        return self

    def query(
        self, predicate: str, args: Optional[List[Any]] = None, min_degree: float = 0.0
    ) -> List[Fact]:
        """
        Query the knowledge base for matching facts.

        Args:
            predicate: Predicate to search for
            args: Arguments to match (can contain variables like '?x')
            min_degree: Minimum degree threshold

        Returns:
            List of matching facts

        Examples:
            >>> # Find all zebras
            >>> inf.query('is-zebra')

            >>> # Find specific fact
            >>> inf.query('is-zebra', ['sam'])

            >>> # Find with minimum certainty
            >>> inf.query('is-zebra', min_degree=0.7)
        """
        results = []
        pattern = Fact(predicate, args or [], 1.0)

        for fact_key, fact in self.facts.items():
            if fact.predicate != predicate:
                continue

            if fact.degree < min_degree:
                continue

            if args:
                matched, _ = fact.matches_pattern(pattern)
                if not matched:
                    continue

            results.append(fact)

        return results

    def ask(self, conditions: List[Union[List, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Ask a question and get all matching variable bindings.

        Args:
            conditions: List of conditions to match

        Returns:
            List of all satisfying variable bindings

        Examples:
            >>> # Who is a tall person?
            >>> inf.ask([
            ...     {'pred': 'is-person', 'args': ['?x']},
            ...     {'pred': 'is-tall', 'args': ['?x']}
            ... ])
        """
        # Convert list format to Condition objects
        condition_objs = []
        for cond in conditions:
            if isinstance(cond, list):
                # Convert ['pred', ['arg1', 'arg2']] format
                if len(cond) >= 2:
                    condition_objs.append(Condition(predicate=cond[0], args=cond[1]))
            elif isinstance(cond, dict):
                condition_objs.append(Condition.from_dict(cond))

        # Run inference first
        self.run()

        # Find all matching bindings
        return self._satisfies_conditions(condition_objs)

    def explain(self, fact: Union[Fact, Dict[str, Any]]) -> List[str]:
        """
        Explain how a fact was derived.

        Args:
            fact: Fact to explain

        Returns:
            List of explanation strings
        """
        # This would require tracking provenance during inference
        # For now, return a simple message
        if isinstance(fact, dict):
            fact = Fact.from_dict(fact)

        key = (fact.predicate, tuple(fact.args))
        if key in self.facts:
            return [f"Fact {fact.predicate}{fact.args} exists with degree {self.facts[key].degree}"]
        else:
            return [f"Fact {fact.predicate}{fact.args} not found in knowledge base"]

    def clear(self) -> "FuzzyInfer":
        """Clear all facts and rules."""
        self.facts.clear()
        self.rules.clear()
        self._rule_history.clear()
        self.inference_log.clear()
        return self

    def get_facts(self) -> List[Fact]:
        """Get all facts in the knowledge base."""
        return list(self.facts.values())

    def get_rules(self) -> List[Rule]:
        """Get all rules in the rule base."""
        return self.rules.copy()

    def __len__(self) -> int:
        """Return the number of facts in the knowledge base."""
        return len(self.facts)

    def __repr__(self) -> str:
        """String representation of the inference engine."""
        return f"FuzzyInfer(facts={len(self.facts)}, rules={len(self.rules)})"
