"""
Knowledge base merging strategies for FuzzyInfer.

Provides various strategies for merging knowledge bases with conflict detection
and resolution.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
import logging

from fuzzy_infer.core import FuzzyInfer, Fact, Rule, Condition

logger = logging.getLogger(__name__)


class MergeStrategy(Enum):
    """Available merge strategies."""
    UNION = "union"  # Keep all facts/rules, max degree for duplicates
    OVERRIDE = "override"  # Second KB takes precedence
    COMPLEMENT = "complement"  # Only add new facts/rules
    WEIGHTED = "weighted"  # Weighted average of degrees
    SMART = "smart"  # Intelligent conflict detection and resolution


@dataclass
class Conflict:
    """Represents a detected conflict between knowledge bases."""
    type: str  # 'fact_contradiction', 'rule_contradiction', 'mutual_exclusion', 'subsumption'
    severity: float  # 0.0 to 1.0
    kb1_item: Any  # Fact or Rule from KB1
    kb2_item: Any  # Fact or Rule from KB2
    description: str
    suggested_resolution: str


class KnowledgeBaseMerger:
    """Handles merging of multiple knowledge bases with conflict detection."""
    
    # Predicates that typically should have single values
    EXCLUSIVE_PREDICATES = {
        'species', 'type', 'category', 'class', 'kind',
        'gender', 'sex', 'color', 'size-category'
    }
    
    # Predicate pairs that are typically contradictory
    CONTRADICTORY_PAIRS = {
        ('is-alive', 'is-dead'),
        ('is-predator', 'is-prey'),
        ('is-carnivore', 'is-herbivore'),
        ('is-dangerous', 'is-safe'),
        ('is-domestic', 'is-wild'),
    }
    
    def __init__(self, threshold: float = 0.5):
        """
        Initialize merger with conflict detection threshold.
        
        Args:
            threshold: Degree difference threshold for conflict detection (default 0.5)
        """
        self.threshold = threshold
        self.conflicts: List[Conflict] = []
    
    def merge(
        self, 
        kb1: FuzzyInfer, 
        kb2: FuzzyInfer,
        strategy: MergeStrategy = MergeStrategy.UNION,
        weights: Optional[Tuple[float, float]] = None,
        auto_resolve: bool = False
    ) -> FuzzyInfer:
        """
        Merge two knowledge bases using specified strategy.
        
        Args:
            kb1: First knowledge base
            kb2: Second knowledge base  
            strategy: Merge strategy to use
            weights: Weights for weighted merge (must sum to 1.0)
            auto_resolve: Automatically resolve conflicts in smart mode
            
        Returns:
            Merged knowledge base
        """
        self.conflicts = []
        
        if strategy == MergeStrategy.SMART:
            return self._smart_merge(kb1, kb2, auto_resolve)
        elif strategy == MergeStrategy.UNION:
            return self._union_merge(kb1, kb2)
        elif strategy == MergeStrategy.OVERRIDE:
            return self._override_merge(kb1, kb2)
        elif strategy == MergeStrategy.COMPLEMENT:
            return self._complement_merge(kb1, kb2)
        elif strategy == MergeStrategy.WEIGHTED:
            if not weights or len(weights) != 2:
                weights = (0.5, 0.5)
            return self._weighted_merge(kb1, kb2, weights)
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
    
    def _union_merge(self, kb1: FuzzyInfer, kb2: FuzzyInfer) -> FuzzyInfer:
        """Simple union merge - combines all facts and rules."""
        result = FuzzyInfer()
        
        # Add all facts from both KBs (fuzzy OR handles duplicates)
        for fact in kb1.get_facts():
            result.add_fact(fact)
        for fact in kb2.get_facts():
            result.add_fact(fact)
        
        # Add all rules from both KBs
        for rule in kb1.get_rules():
            result.add_rule(rule)
        for rule in kb2.get_rules():
            result.add_rule(rule)
        
        return result
    
    def _override_merge(self, kb1: FuzzyInfer, kb2: FuzzyInfer) -> FuzzyInfer:
        """Override merge - KB2 takes precedence."""
        result = FuzzyInfer()
        
        # Track what KB2 provides
        kb2_fact_keys = set()
        kb2_rule_names = set()
        
        # Add all facts from KB2
        for fact in kb2.get_facts():
            result.add_fact(fact)
            kb2_fact_keys.add((fact.predicate, tuple(fact.args)))
        
        # Add facts from KB1 that aren't in KB2
        for fact in kb1.get_facts():
            key = (fact.predicate, tuple(fact.args))
            if key not in kb2_fact_keys:
                result.add_fact(fact)
        
        # Add all rules from KB2
        for rule in kb2.get_rules():
            result.add_rule(rule)
            if rule.name:
                kb2_rule_names.add(rule.name)
        
        # Add rules from KB1 that don't have name conflicts
        for rule in kb1.get_rules():
            if not rule.name or rule.name not in kb2_rule_names:
                result.add_rule(rule)
        
        return result
    
    def _complement_merge(self, kb1: FuzzyInfer, kb2: FuzzyInfer) -> FuzzyInfer:
        """Complement merge - only add new items from KB2."""
        result = FuzzyInfer()
        
        # Add all facts from KB1
        kb1_fact_keys = set()
        for fact in kb1.get_facts():
            result.add_fact(fact)
            kb1_fact_keys.add((fact.predicate, tuple(fact.args)))
        
        # Only add new facts from KB2
        for fact in kb2.get_facts():
            key = (fact.predicate, tuple(fact.args))
            if key not in kb1_fact_keys:
                result.add_fact(fact)
        
        # Add all rules from KB1
        kb1_rule_names = set()
        for rule in kb1.get_rules():
            result.add_rule(rule)
            if rule.name:
                kb1_rule_names.add(rule.name)
        
        # Only add new rules from KB2
        for rule in kb2.get_rules():
            if not rule.name or rule.name not in kb1_rule_names:
                result.add_rule(rule)
        
        return result
    
    def _weighted_merge(
        self, 
        kb1: FuzzyInfer, 
        kb2: FuzzyInfer,
        weights: Tuple[float, float]
    ) -> FuzzyInfer:
        """Weighted merge - combine degrees using weights."""
        result = FuzzyInfer()
        w1, w2 = weights
        
        # Normalize weights
        total = w1 + w2
        w1, w2 = w1/total, w2/total
        
        # Collect all fact keys
        all_facts = {}
        
        for fact in kb1.get_facts():
            key = (fact.predicate, tuple(fact.args))
            all_facts[key] = {'kb1': fact.degree, 'kb2': 0.0}
        
        for fact in kb2.get_facts():
            key = (fact.predicate, tuple(fact.args))
            if key in all_facts:
                all_facts[key]['kb2'] = fact.degree
            else:
                all_facts[key] = {'kb1': 0.0, 'kb2': fact.degree}
        
        # Add weighted facts
        for (pred, args), degrees in all_facts.items():
            weighted_degree = w1 * degrees['kb1'] + w2 * degrees['kb2']
            result.add_fact(Fact(pred, list(args), weighted_degree))
        
        # For rules, use union approach
        for rule in kb1.get_rules():
            result.add_rule(rule)
        for rule in kb2.get_rules():
            result.add_rule(rule)
        
        return result
    
    def _smart_merge(
        self, 
        kb1: FuzzyInfer, 
        kb2: FuzzyInfer,
        auto_resolve: bool
    ) -> FuzzyInfer:
        """
        Smart merge with conflict detection and resolution.
        """
        # Detect conflicts
        self._detect_fact_conflicts(kb1, kb2)
        self._detect_rule_conflicts(kb1, kb2)
        self._detect_semantic_conflicts(kb1, kb2)
        
        # Sort conflicts by severity
        self.conflicts.sort(key=lambda c: c.severity, reverse=True)
        
        # Log conflicts
        if self.conflicts:
            logger.warning(f"Detected {len(self.conflicts)} conflicts during merge")
            for conflict in self.conflicts[:5]:  # Show top 5
                logger.warning(f"  - {conflict.type}: {conflict.description}")
        
        # Build merged KB
        result = FuzzyInfer()
        
        # Handle facts with conflict resolution
        fact_conflicts = {
            (c.kb1_item.predicate, tuple(c.kb1_item.args)): c
            for c in self.conflicts 
            if c.type == 'fact_contradiction' and isinstance(c.kb1_item, Fact)
        }
        
        # Add facts from KB1
        for fact in kb1.get_facts():
            key = (fact.predicate, tuple(fact.args))
            if key in fact_conflicts:
                conflict = fact_conflicts[key]
                if auto_resolve:
                    # Use resolution strategy
                    resolved_fact = self._resolve_fact_conflict(
                        fact, conflict.kb2_item, conflict
                    )
                    result.add_fact(resolved_fact)
                else:
                    # Keep higher confidence fact
                    if fact.degree >= conflict.kb2_item.degree:
                        result.add_fact(fact)
            else:
                result.add_fact(fact)
        
        # Add non-conflicting facts from KB2
        kb1_keys = {(f.predicate, tuple(f.args)) for f in kb1.get_facts()}
        for fact in kb2.get_facts():
            key = (fact.predicate, tuple(fact.args))
            if key not in kb1_keys:
                result.add_fact(fact)
            elif key not in fact_conflicts:
                # Let fuzzy OR handle it
                result.add_fact(fact)
        
        # Handle rules
        rule_conflicts = {
            c.kb1_item.name: c
            for c in self.conflicts
            if c.type in ['rule_contradiction', 'subsumption'] and 
               isinstance(c.kb1_item, Rule) and c.kb1_item.name
        }
        
        # Add rules with conflict handling
        for rule in kb1.get_rules():
            if rule.name in rule_conflicts:
                conflict = rule_conflicts[rule.name]
                if auto_resolve:
                    resolved_rule = self._resolve_rule_conflict(
                        rule, conflict.kb2_item, conflict
                    )
                    result.add_rule(resolved_rule)
                else:
                    # Keep higher priority rule
                    if rule.priority >= conflict.kb2_item.priority:
                        result.add_rule(rule)
            else:
                result.add_rule(rule)
        
        # Add non-conflicting rules from KB2
        kb1_rule_names = {r.name for r in kb1.get_rules() if r.name}
        for rule in kb2.get_rules():
            if not rule.name or rule.name not in kb1_rule_names:
                result.add_rule(rule)
        
        return result
    
    def _detect_fact_conflicts(self, kb1: FuzzyInfer, kb2: FuzzyInfer):
        """Detect contradictory facts between KBs."""
        kb1_facts = {(f.predicate, tuple(f.args)): f for f in kb1.get_facts()}
        
        for fact2 in kb2.get_facts():
            key = (fact2.predicate, tuple(fact2.args))
            
            if key in kb1_facts:
                fact1 = kb1_facts[key]
                degree_diff = abs(fact1.degree - fact2.degree)
                
                # Check for significant contradiction
                if degree_diff > self.threshold:
                    self.conflicts.append(Conflict(
                        type='fact_contradiction',
                        severity=degree_diff,
                        kb1_item=fact1,
                        kb2_item=fact2,
                        description=f"{fact1.predicate}{fact1.args}: {fact1.degree:.2f} vs {fact2.degree:.2f}",
                        suggested_resolution=f"Use {'KB1' if fact1.degree > fact2.degree else 'KB2'} value or average"
                    ))
            
            # Check for mutual exclusions
            if fact2.predicate in self.EXCLUSIVE_PREDICATES:
                for (pred1, args1), fact1 in kb1_facts.items():
                    if pred1 == fact2.predicate and args1[0] == fact2.args[0] and args1[1] != fact2.args[1]:
                        # Same predicate, same subject, different value
                        self.conflicts.append(Conflict(
                            type='mutual_exclusion',
                            severity=0.8,
                            kb1_item=fact1,
                            kb2_item=fact2,
                            description=f"Exclusive values for {pred1}({args1[0]}): {args1[1]} vs {fact2.args[1]}",
                            suggested_resolution="Choose one value or create uncertainty"
                        ))
    
    def _detect_rule_conflicts(self, kb1: FuzzyInfer, kb2: FuzzyInfer):
        """Detect conflicting rules between KBs."""
        kb1_rules = kb1.get_rules()
        kb2_rules = kb2.get_rules()
        
        # Check rules with same name
        kb1_named = {r.name: r for r in kb1_rules if r.name}
        for rule2 in kb2_rules:
            if rule2.name and rule2.name in kb1_named:
                rule1 = kb1_named[rule2.name]
                
                # Compare rule structure
                if not self._rules_equivalent(rule1, rule2):
                    self.conflicts.append(Conflict(
                        type='rule_contradiction',
                        severity=0.7,
                        kb1_item=rule1,
                        kb2_item=rule2,
                        description=f"Different implementations of rule '{rule1.name}'",
                        suggested_resolution="Rename one rule or merge logic"
                    ))
        
        # Check for subsumption (one rule more general than another)
        for rule1 in kb1_rules:
            for rule2 in kb2_rules:
                if self._rule_subsumes(rule1, rule2):
                    self.conflicts.append(Conflict(
                        type='subsumption',
                        severity=0.4,
                        kb1_item=rule1,
                        kb2_item=rule2,
                        description=f"Rule '{rule1.name or 'unnamed'}' subsumes '{rule2.name or 'unnamed'}'",
                        suggested_resolution="Keep more specific rule or both"
                    ))
    
    def _detect_semantic_conflicts(self, kb1: FuzzyInfer, kb2: FuzzyInfer):
        """Detect semantic/logical conflicts between KBs."""
        all_facts = list(kb1.get_facts()) + list(kb2.get_facts())
        
        # Check for contradictory predicate pairs
        for pred1, pred2 in self.CONTRADICTORY_PAIRS:
            facts1 = [f for f in all_facts if f.predicate == pred1]
            facts2 = [f for f in all_facts if f.predicate == pred2]
            
            for f1 in facts1:
                for f2 in facts2:
                    if f1.args == f2.args and f1.degree > 0.5 and f2.degree > 0.5:
                        self.conflicts.append(Conflict(
                            type='semantic_contradiction',
                            severity=0.9,
                            kb1_item=f1,
                            kb2_item=f2,
                            description=f"Contradictory facts: {pred1}{f1.args} and {pred2}{f2.args}",
                            suggested_resolution="Review domain logic"
                        ))
    
    def _rules_equivalent(self, rule1: Rule, rule2: Rule) -> bool:
        """Check if two rules are functionally equivalent."""
        # Simple check - could be made more sophisticated
        return (len(rule1.conditions) == len(rule2.conditions) and
                len(rule1.actions) == len(rule2.actions) and
                rule1.priority == rule2.priority)
    
    def _rule_subsumes(self, rule1: Rule, rule2: Rule) -> bool:
        """Check if rule1 subsumes rule2 (more general conditions)."""
        # Check if rule1's conditions are subset of rule2's
        if len(rule1.conditions) >= len(rule2.conditions):
            return False
        
        # Simple subsumption check - could be enhanced
        rule1_preds = {c.predicate for c in rule1.conditions}
        rule2_preds = {c.predicate for c in rule2.conditions}
        
        return rule1_preds.issubset(rule2_preds)
    
    def _resolve_fact_conflict(
        self, 
        fact1: Fact, 
        fact2: Fact, 
        conflict: Conflict
    ) -> Fact:
        """Resolve a fact conflict based on the conflict type."""
        if conflict.type == 'fact_contradiction':
            # Average the degrees for moderate conflicts
            if conflict.severity < 0.7:
                avg_degree = (fact1.degree + fact2.degree) / 2
                return Fact(fact1.predicate, fact1.args, avg_degree)
            else:
                # Use higher confidence for severe conflicts
                return fact1 if fact1.degree > fact2.degree else fact2
        
        return fact1  # Default to first KB
    
    def _resolve_rule_conflict(
        self,
        rule1: Rule,
        rule2: Rule, 
        conflict: Conflict
    ) -> Rule:
        """Resolve a rule conflict."""
        if conflict.type == 'subsumption':
            # Keep more specific rule
            return rule2 if len(rule2.conditions) > len(rule1.conditions) else rule1
        elif conflict.type == 'rule_contradiction':
            # Keep higher priority rule
            return rule1 if rule1.priority > rule2.priority else rule2
        
        return rule1  # Default to first KB
    
    def get_conflict_report(self) -> str:
        """Generate a human-readable conflict report."""
        if not self.conflicts:
            return "No conflicts detected."
        
        report = f"Detected {len(self.conflicts)} conflicts:\n\n"
        
        # Group by type
        by_type = {}
        for c in self.conflicts:
            if c.type not in by_type:
                by_type[c.type] = []
            by_type[c.type].append(c)
        
        for conflict_type, conflicts in by_type.items():
            report += f"{conflict_type.replace('_', ' ').title()} ({len(conflicts)}):\n"
            for c in conflicts[:3]:  # Show up to 3 examples
                report += f"  - {c.description}\n"
                report += f"    Suggested: {c.suggested_resolution}\n"
            if len(conflicts) > 3:
                report += f"  ... and {len(conflicts)-3} more\n"
            report += "\n"
        
        return report