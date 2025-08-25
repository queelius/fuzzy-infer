#!/usr/bin/env python3
"""
Basic example of using FuzzyInfer for classical logic inference.

This example demonstrates:
- Creating facts and rules
- Running inference
- Querying results
"""

from fuzzy_infer import Fact, FuzzyInfer, Rule
from fuzzy_infer.models import Action, Condition


def main():
    # Create an inference engine
    inf = FuzzyInfer()

    # Add some facts about Socrates
    inf.add_facts([
        Fact("is-human", ["socrates"], 1.0),
        Fact("is-greek", ["socrates"], 1.0),
    ])

    # Add a rule: All humans are mortal
    rule = Rule(
        conditions=[Condition(predicate="is-human", args=["?x"])],
        actions=[Action("add", {"pred": "is-mortal", "args": ["?x"]})],
        name="human-mortality"
    )
    inf.add_rule(rule)

    # Add another rule: Greeks are philosophers
    rule2 = Rule(
        conditions=[
            Condition(predicate="is-greek", args=["?x"]),
            Condition(predicate="is-human", args=["?x"])
        ],
        actions=[Action("add", {"pred": "is-philosopher", "args": ["?x"]})],
        name="greek-philosopher"
    )
    inf.add_rule(rule2)

    print("Initial facts:")
    for fact in inf.get_facts():
        print(f"  {fact.predicate}({', '.join(fact.args)}) = {fact.degree}")

    # Run inference
    print("\nRunning inference...")
    inf.run()

    print("\nFacts after inference:")
    for fact in inf.get_facts():
        print(f"  {fact.predicate}({', '.join(fact.args)}) = {fact.degree}")

    # Query specific facts
    print("\nQueries:")
    mortal = inf.query("is-mortal", ["socrates"])
    if mortal:
        print(f"  Is Socrates mortal? Yes (degree: {mortal[0].degree})")
    
    philosopher = inf.query("is-philosopher", ["socrates"])
    if philosopher:
        print(f"  Is Socrates a philosopher? Yes (degree: {philosopher[0].degree})")


if __name__ == "__main__":
    main()