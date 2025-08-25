"""
Serialization module for FuzzyInfer.

Provides JSON and YAML serialization/deserialization for facts and rules.
"""

import json
from pathlib import Path
from typing import List, TextIO, Union

from fuzzy_infer.core import FuzzyInfer
from fuzzy_infer.models import Fact, Rule


class FuzzyInferSerializer:
    """Handles serialization and deserialization of FuzzyInfer components."""

    @staticmethod
    def to_dict(inf: FuzzyInfer) -> dict:
        """
        Convert FuzzyInfer instance to dictionary.

        Args:
            inf: FuzzyInfer instance

        Returns:
            Dictionary representation
        """
        return {
            "facts": [fact.to_dict() for fact in inf.get_facts()],
            "rules": [rule.to_dict() for rule in inf.get_rules()]
        }

    @staticmethod
    def from_dict(data: dict) -> FuzzyInfer:
        """
        Create FuzzyInfer instance from dictionary.

        Args:
            data: Dictionary containing facts and rules

        Returns:
            FuzzyInfer instance
        """
        inf = FuzzyInfer()
        
        # Add facts
        for fact_dict in data["facts"]:
            inf.add_fact(Fact.from_dict(fact_dict))
        
        # Add rules
        for rule_dict in data["rules"]:
            inf.add_rule(Rule.from_dict(rule_dict))
        
        return inf

    @staticmethod
    def to_json(inf: FuzzyInfer, indent: int = 2) -> str:
        """
        Convert FuzzyInfer instance to JSON string.

        Args:
            inf: FuzzyInfer instance
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(FuzzyInferSerializer.to_dict(inf), indent=indent)

    @staticmethod
    def from_json(json_str: str) -> FuzzyInfer:
        """
        Create FuzzyInfer instance from JSON string.

        Args:
            json_str: JSON string

        Returns:
            FuzzyInfer instance
        """
        data = json.loads(json_str)
        return FuzzyInferSerializer.from_dict(data)

    @staticmethod
    def to_yaml(inf: FuzzyInfer) -> str:
        """
        Convert FuzzyInfer instance to YAML string.

        Args:
            inf: FuzzyInfer instance

        Returns:
            YAML string representation
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML serialization")
        
        return yaml.dump(FuzzyInferSerializer.to_dict(inf), default_flow_style=False)

    @staticmethod
    def from_yaml(yaml_str: str) -> FuzzyInfer:
        """
        Create FuzzyInfer instance from YAML string.

        Args:
            yaml_str: YAML string

        Returns:
            FuzzyInfer instance
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML deserialization")
        
        data = yaml.safe_load(yaml_str)
        return FuzzyInferSerializer.from_dict(data)

    @staticmethod
    def facts_to_json(facts: List[Fact], indent: int = 2) -> str:
        """
        Convert a list of facts to JSON string.

        Args:
            facts: List of Fact objects
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        fact_dicts = [fact.to_dict() for fact in facts]
        return json.dumps(fact_dicts, indent=indent)

    @staticmethod
    def facts_from_json(json_str: str) -> List[Fact]:
        """
        Create facts from JSON string.

        Args:
            json_str: JSON string containing fact data

        Returns:
            List of Fact objects
        """
        fact_dicts = json.loads(json_str)
        return [Fact.from_dict(d) for d in fact_dicts]

    @staticmethod
    def rules_to_json(rules: List[Rule], indent: int = 2) -> str:
        """
        Convert a list of rules to JSON string.

        Args:
            rules: List of Rule objects
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        rule_dicts = [rule.to_dict() for rule in rules]
        return json.dumps(rule_dicts, indent=indent)

    @staticmethod
    def rules_from_json(json_str: str) -> List[Rule]:
        """
        Create rules from JSON string.

        Args:
            json_str: JSON string containing rule data

        Returns:
            List of Rule objects
        """
        rule_dicts = json.loads(json_str)
        return [Rule.from_dict(d) for d in rule_dicts]

    @staticmethod
    def knowledge_base_to_json(inf: FuzzyInfer, indent: int = 2) -> str:
        """
        Serialize entire knowledge base to JSON.

        Args:
            inf: FuzzyInfer instance
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        kb = {
            "facts": [fact.to_dict() for fact in inf.get_facts()],
            "rules": [rule.to_dict() for rule in inf.get_rules()],
            "metadata": {
                "version": "0.1.0",
                "num_facts": len(inf.facts),
                "num_rules": len(inf.rules),
            },
        }
        return json.dumps(kb, indent=indent)

    @staticmethod
    def knowledge_base_from_json(json_str: str) -> FuzzyInfer:
        """
        Create FuzzyInfer instance from JSON.

        Args:
            json_str: JSON string containing knowledge base

        Returns:
            FuzzyInfer instance with loaded data
        """
        kb = json.loads(json_str)
        inf = FuzzyInfer()

        if "facts" in kb:
            facts = [Fact.from_dict(d) for d in kb["facts"]]
            inf.add_facts(facts)

        if "rules" in kb:
            rules = [Rule.from_dict(d) for d in kb["rules"]]
            inf.add_rules(rules)

        return inf

    @staticmethod
    def save_to_file(inf: FuzzyInfer, filepath: Union[str, Path]) -> None:
        """
        Save knowledge base to file.

        Args:
            inf: FuzzyInfer instance
            filepath: Path to save file
            
        Raises:
            ValueError: If file format is not supported
        """
        filepath = Path(filepath)
        
        # Check for supported formats
        if filepath.suffix in [".yaml", ".yml"]:
            with open(filepath, "w") as f:
                FuzzyInferSerializer._save_yaml(inf, f)
        elif filepath.suffix in [".json"]:
            with open(filepath, "w") as f:
                f.write(FuzzyInferSerializer.knowledge_base_to_json(inf))
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}. Use .json, .yaml, or .yml")

    @staticmethod
    def load_from_file(filepath: Union[str, Path]) -> FuzzyInfer:
        """
        Load knowledge base from file.

        Args:
            filepath: Path to load file

        Returns:
            FuzzyInfer instance with loaded data
        """
        filepath = Path(filepath)
        with open(filepath) as f:
            if filepath.suffix == ".yaml" or filepath.suffix == ".yml":
                return FuzzyInferSerializer._load_yaml(f)
            else:
                return FuzzyInferSerializer.knowledge_base_from_json(f.read())

    @staticmethod
    def _save_yaml(inf: FuzzyInfer, file: TextIO) -> None:
        """Save to YAML format (requires PyYAML)."""
        try:
            import yaml

            kb = {
                "facts": [fact.to_dict() for fact in inf.get_facts()],
                "rules": [rule.to_dict() for rule in inf.get_rules()],
                "metadata": {
                    "version": "0.1.0",
                    "num_facts": len(inf.facts),
                    "num_rules": len(inf.rules),
                },
            }
            yaml.dump(kb, file, default_flow_style=False, sort_keys=False)
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML serialization. Install with: pip install pyyaml"
            )

    @staticmethod
    def _load_yaml(file: TextIO) -> FuzzyInfer:
        """Load from YAML format (requires PyYAML)."""
        try:
            import yaml

            kb = yaml.safe_load(file)
            inf = FuzzyInfer()

            if kb and "facts" in kb:
                facts = [Fact.from_dict(d) for d in kb["facts"]]
                inf.add_facts(facts)

            if kb and "rules" in kb:
                rules = [Rule.from_dict(d) for d in kb["rules"]]
                inf.add_rules(rules)

            return inf
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML deserialization. Install with: pip install pyyaml"
            )
