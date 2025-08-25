#!/usr/bin/env python3
"""
Example using the fluent API and RuleBuilder DSL.

This demonstrates:
- Fluent/chainable API
- RuleBuilder for creating rules
- Context manager usage
"""

from fuzzy_infer import Fact, FuzzyInfer
from fuzzy_infer.models import RuleBuilder


def main():
    print("=" * 60)
    print("Example 1: Fluent API with method chaining")
    print("=" * 60)
    
    # Everything in one fluent chain
    results = (
        FuzzyInfer()
        .add_fact(Fact("is-bird", ["tweety"], 0.9))
        .add_fact(Fact("is-yellow", ["tweety"], 1.0))
        .add_fact(Fact("has-wings", ["tweety"], 0.95))
        .add_rule(
            RuleBuilder()
            .when("is-bird", ["?x"])
            .with_degree_greater_than(0.8)
            .then_add("can-fly", ["?x"])
            .with_degree_multiplied_by(0.9)
            .named("birds-fly")
            .build()
        )
        .add_rule(
            RuleBuilder()
            .when("is-bird", ["?x"])
            .when("is-yellow", ["?x"])
            .then_add("is-canary", ["?x"])
            .with_degree_multiplied_by(0.95)
            .build()
        )
        .run()
        .query("can-fly", ["tweety"])
    )
    
    if results:
        print(f"Can Tweety fly? Yes (confidence: {results[0].degree:.2%})")

    print("\n" + "=" * 60)
    print("Example 2: Context manager with RuleBuilder DSL")
    print("=" * 60)
    
    # Using context manager for automatic cleanup
    with FuzzyInfer.session() as inf:
        # Add facts about animals
        inf.add_fact(Fact("has-stripes", ["tiger"], 1.0))
        inf.add_fact(Fact("is-large", ["tiger"], 0.9))
        inf.add_fact(Fact("eats-meat", ["tiger"], 1.0))
        
        # Build complex rules using the DSL
        carnivore_rule = (
            RuleBuilder()
            .when("eats-meat", ["?animal"])
            .then_add("is-carnivore", ["?animal"])
            .named("carnivore-classification")
            .build()
        )
        
        dangerous_rule = (
            RuleBuilder()
            .when("is-carnivore", ["?x"])
            .when("is-large", ["?x"])
            .with_degree_greater_than(0.7)
            .then_add("is-dangerous", ["?x"])
            .with_degree_multiplied_by(0.95)
            .named("danger-assessment")
            .with_priority(10)  # Higher priority
            .build()
        )
        
        inf.add_rule(carnivore_rule)
        inf.add_rule(dangerous_rule)
        inf.run()
        
        # Query results
        dangerous = inf.query("is-dangerous", ["tiger"])
        if dangerous:
            print(f"Is tiger dangerous? Yes (confidence: {dangerous[0].degree:.2%})")

    print("\n" + "=" * 60)
    print("Example 3: Complex rule with logical operators")
    print("=" * 60)
    
    inf = FuzzyInfer()
    
    # Add facts about different animals
    inf.add_facts([
        Fact("has-wings", ["eagle"], 1.0),
        Fact("is-airplane", ["boeing747"], 1.0),
        Fact("is-superhero", ["superman"], 1.0),
        Fact("has-cape", ["superman"], 1.0),
    ])
    
    # Rule with OR conditions - anything that can fly
    flying_rule = {
        "name": "can-fly-rule",
        "cond": [
            {
                "or": [
                    {"pred": "has-wings", "args": ["?x"]},
                    {"pred": "is-airplane", "args": ["?x"]},
                    {"pred": "is-superhero", "args": ["?x"]}
                ]
            }
        ],
        "actions": [
            {"action": "add", "fact": {"pred": "can-fly", "args": ["?x"], "deg": 0.95}}
        ]
    }
    
    inf.add_rule(flying_rule)
    inf.run()
    
    # Check what can fly
    for entity in ["eagle", "boeing747", "superman"]:
        result = inf.query("can-fly", [entity])
        if result:
            print(f"{entity} can fly: {result[0].degree:.2%}")


if __name__ == "__main__":
    main()