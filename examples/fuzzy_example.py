#!/usr/bin/env python3
"""
Fuzzy logic example demonstrating uncertainty and degree propagation.

This example shows:
- Fuzzy facts with degrees of belief
- Degree calculations in rules
- Fuzzy inference
"""

from fuzzy_infer import Fact, FuzzyInfer, Rule
from fuzzy_infer.models import Action, Condition


def main():
    # Create an inference engine
    inf = FuzzyInfer()

    # Add fuzzy facts about weather
    inf.add_facts([
        Fact("is-cloudy", ["today"], 0.8),
        Fact("is-humid", ["today"], 0.7),
        Fact("low-pressure", ["today"], 0.6),
    ])

    # Rule: If cloudy AND humid, then likely to rain
    # Rain likelihood = min(cloudy, humid) * 0.9
    rule1 = Rule(
        conditions=[
            Condition(predicate="is-cloudy", args=["?day"], degree_var="?c"),
            Condition(predicate="is-humid", args=["?day"], degree_var="?h")
        ],
        actions=[
            Action("add", {
                "pred": "will-rain",
                "args": ["?day"],
                "deg": ["*", ["min", "?c", "?h"], 0.9]
            })
        ],
        name="rain-prediction"
    )
    inf.add_rule(rule1)

    # Rule: If low pressure, increase rain likelihood
    rule2 = Rule(
        conditions=[
            Condition(predicate="low-pressure", args=["?day"], degree_var="?p")
        ],
        actions=[
            Action("add", {
                "pred": "will-rain",
                "args": ["?day"],
                "deg": ["*", "?p", 0.8]
            })
        ],
        name="pressure-rain"
    )
    inf.add_rule(rule2)

    # Rule: If will rain with high certainty, suggest umbrella
    rule3 = Rule(
        conditions=[
            Condition(
                predicate="will-rain",
                args=["?day"],
                degree_var="?r",
                degree_constraint=[">", "?r", 0.5]
            )
        ],
        actions=[
            Action("add", {
                "pred": "need-umbrella",
                "args": ["?day"],
                "deg": "?r"
            })
        ],
        name="umbrella-suggestion"
    )
    inf.add_rule(rule3)

    print("Initial weather conditions:")
    for fact in inf.get_facts():
        print(f"  {fact.predicate}({', '.join(fact.args)}) = {fact.degree:.2f}")

    # Run inference
    print("\nRunning fuzzy inference...")
    inf.run()

    print("\nResults after inference:")
    for fact in inf.get_facts():
        print(f"  {fact.predicate}({', '.join(fact.args)}) = {fact.degree:.2f}")

    # Query specific predictions
    print("\nPredictions:")
    rain = inf.query("will-rain", ["today"])
    if rain:
        # Note: Multiple rules may have added rain facts, FuzzyInfer takes the maximum
        print(f"  Rain likelihood: {rain[0].degree:.2%}")
    
    umbrella = inf.query("need-umbrella", ["today"])
    if umbrella:
        print(f"  Need umbrella: {umbrella[0].degree:.2%}")


if __name__ == "__main__":
    main()