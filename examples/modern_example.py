#!/usr/bin/env python3
"""
Modern example demonstrating the pythonic API of FuzzyInfer.

This example shows how to use the fluent API, RuleBuilder, and
context managers for clean, readable fuzzy inference code.
"""

from fuzzy_infer import FuzzyInfer, Fact, RuleBuilder


def animal_classification_example():
    """Demonstrate fuzzy animal classification."""
    print("=== Animal Classification Example ===\n")
    
    # Using fluent API to build and run inference
    inf = (FuzzyInfer()
        # Add observed facts about an animal
        .add_fact(Fact('has-fur', ['animal-1'], 0.9))
        .add_fact(Fact('has-stripes', ['animal-1'], 0.7))
        .add_fact(Fact('is-large', ['animal-1'], 0.8))
        .add_fact(Fact('eats-meat', ['animal-1'], 0.6))
        
        # Add classification rules using RuleBuilder
        .add_rule(
            RuleBuilder()
            .named('mammal-rule')
            .when('has-fur', ['?x'])
            .with_degree_greater_than(0.7)
            .then_add('is-mammal', ['?x'])
            .with_degree_multiplied_by(0.95)
            .build()
        )
        .add_rule(
            RuleBuilder()
            .named('tiger-rule')
            .when('is-mammal', ['?x'])
            .when('has-stripes', ['?x'])
            .with_degree_greater_than(0.6)
            .when('is-large', ['?x'])
            .then_add('might-be-tiger', ['?x'])
            .with_degree_multiplied_by(0.9)
            .build()
        )
        .add_rule(
            RuleBuilder()
            .named('carnivore-rule')
            .when('eats-meat', ['?x'])
            .with_degree_greater_than(0.5)
            .then_add('is-carnivore', ['?x'])
            .build()
        )
        .add_rule(
            RuleBuilder()
            .named('predator-rule')
            .when('is-carnivore', ['?x'])
            .when('might-be-tiger', ['?x'])
            .then_add('is-predator', ['?x'])
            .with_degree_multiplied_by(0.95)
            .with_priority(10)
            .build()
        ))
    
    # Run inference
    inf.run()
    
    # Query results
    print("Inference Results:")
    print("-" * 40)
    
    for predicate in ['is-mammal', 'might-be-tiger', 'is-carnivore', 'is-predator']:
        results = inf.query(predicate, ['animal-1'])
        if results:
            degree = results[0].degree
            print(f"{predicate:20} : {degree:.3f} ({degree*100:.1f}% certain)")
        else:
            print(f"{predicate:20} : Not inferred")
    
    print()


def medical_diagnosis_example():
    """Demonstrate medical diagnosis with fuzzy symptoms."""
    print("=== Medical Diagnosis Example ===\n")
    
    with FuzzyInfer.session() as session:
        # Patient symptoms (with uncertainty)
        session.add_facts([
            Fact('has-fever', ['patient-x'], 0.85),
            Fact('has-headache', ['patient-x'], 0.9),
            Fact('has-cough', ['patient-x'], 0.3),
            Fact('has-fatigue', ['patient-x'], 0.7),
            Fact('has-sore-throat', ['patient-x'], 0.8),
        ])
        
        # Medical rules
        session.add_rule(
            RuleBuilder()
            .named('flu-diagnosis')
            .when('has-fever', ['?p'])
            .with_degree_greater_than(0.7)
            .when('has-headache', ['?p'])
            .with_degree_greater_than(0.6)
            .when('has-fatigue', ['?p'])
            .then_add('possible-flu', ['?p'])
            .with_degree_multiplied_by(0.85)
            .build()
        )
        
        session.add_rule(
            RuleBuilder()
            .named('strep-throat-diagnosis')
            .when('has-fever', ['?p'])
            .with_degree_greater_than(0.7)
            .when('has-sore-throat', ['?p'])
            .with_degree_greater_than(0.7)
            .when_not('has-cough', ['?p'])  # Strep usually doesn't have cough
            .then_add('possible-strep', ['?p'])
            .with_degree_multiplied_by(0.9)
            .build()
        )
        
        session.add_rule(
            RuleBuilder()
            .named('treatment-recommendation')
            .when('possible-flu', ['?p'])
            .with_degree_greater_than(0.6)
            .then_add('recommend-rest', ['?p'])
            .then_add('recommend-fluids', ['?p'])
            .build()
        )
        
        # Run diagnosis
        session.run()
        
        # Display results
        print("Diagnosis Results for Patient X:")
        print("-" * 40)
        
        diagnoses = ['possible-flu', 'possible-strep', 'recommend-rest', 'recommend-fluids']
        for diagnosis in diagnoses:
            results = session.query(diagnosis, ['patient-x'])
            if results:
                degree = results[0].degree
                confidence = "High" if degree > 0.7 else "Moderate" if degree > 0.4 else "Low"
                print(f"{diagnosis:20} : {degree:.3f} ({confidence} confidence)")
            else:
                print(f"{diagnosis:20} : Not indicated")
    
    print()


def weather_prediction_example():
    """Demonstrate weather prediction with multiple factors."""
    print("=== Weather Prediction Example ===\n")
    
    inf = FuzzyInfer()
    
    # Weather observations
    observations = [
        Fact('humidity-high', ['today'], 0.92),
        Fact('pressure-dropping', ['today'], 0.75),
        Fact('clouds-increasing', ['today'], 0.8),
        Fact('wind-speed-increasing', ['today'], 0.6),
        Fact('temperature-dropping', ['today'], 0.4),
    ]
    
    # Add observations
    for obs in observations:
        inf.add_fact(obs)
        print(f"Observation: {obs.predicate:25} = {obs.degree:.2f}")
    
    print("\nApplying weather prediction rules...")
    
    # Weather prediction rules
    rules = [
        RuleBuilder()
        .named('rain-prediction')
        .when('humidity-high', ['?day'])
        .with_degree_greater_than(0.8)
        .when('pressure-dropping', ['?day'])
        .with_degree_greater_than(0.6)
        .then_add('rain-likely', ['?day'])
        .with_degree_multiplied_by(0.9)
        .build(),
        
        RuleBuilder()
        .named('storm-prediction')
        .when('rain-likely', ['?day'])
        .when('wind-speed-increasing', ['?day'])
        .with_degree_greater_than(0.5)
        .when('clouds-increasing', ['?day'])
        .with_degree_greater_than(0.7)
        .then_add('storm-possible', ['?day'])
        .with_degree_multiplied_by(0.85)
        .build(),
        
        RuleBuilder()
        .named('severe-weather')
        .when('storm-possible', ['?day'])
        .with_degree_greater_than(0.5)
        .then_add('issue-weather-advisory', ['?day'])
        .build(),
    ]
    
    for rule in rules:
        inf.add_rule(rule)
    
    # Run prediction
    inf.run()
    
    print("\nWeather Predictions:")
    print("-" * 40)
    
    predictions = [
        ('rain-likely', 'Rain'),
        ('storm-possible', 'Storm'),
        ('issue-weather-advisory', 'Weather Advisory')
    ]
    
    for pred_name, display_name in predictions:
        results = inf.query(pred_name, ['today'])
        if results:
            degree = results[0].degree
            probability = degree * 100
            print(f"{display_name:20} : {probability:.1f}% chance")
        else:
            print(f"{display_name:20} : No indication")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("FuzzyInfer Modern Examples")
    print("=" * 50 + "\n")
    
    animal_classification_example()
    medical_diagnosis_example()
    weather_prediction_example()
    
    print("=" * 50)
    print("Examples completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()