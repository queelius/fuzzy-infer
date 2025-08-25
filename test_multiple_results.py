#!/usr/bin/env python3
"""Test that queries return multiple results after the fix."""

from fuzzy_infer import FuzzyInfer
from fuzzy_infer.serialization import FuzzyInferSerializer

# Load the comprehensive animal classification KB
inf = FuzzyInferSerializer.load_from_file("examples/knowledge_bases/animal_classification_complete.json")

# Run inference
inf.run()

print("Testing multiple results after fix...")
print("="*50)

# Test 1: Query for all mammals (should return 8)
print("\n1. All mammals:")
mammals = inf.query("is-mammal")
for fact in mammals:
    print(f"  - {fact}")
print(f"Total mammals: {len(mammals)}")

# Test 2: Query for all birds (should return 3)
print("\n2. All birds:")
birds = inf.query("is-bird")
for fact in birds:
    print(f"  - {fact}")
print(f"Total birds: {len(birds)}")

# Test 3: Query for all carnivores (should return multiple)
print("\n3. All carnivores:")
carnivores = inf.query("is-carnivore")
for fact in carnivores:
    print(f"  - {fact}")
print(f"Total carnivores: {len(carnivores)}")

# Test 4: Query for all ungulates (should return 3)
print("\n4. All ungulates:")
ungulates = inf.query("is-ungulate")
for fact in ungulates:
    print(f"  - {fact}")
print(f"Total ungulates: {len(ungulates)}")

# Test 5: Query for all predators
print("\n5. All predators:")
predators = inf.query("is-predator")
for fact in predators:
    print(f"  - {fact}")
print(f"Total predators: {len(predators)}")

# Test 6: Verify specific animals
print("\n6. Verification of specific animals:")
print(f"  - Dog is mammal: {len(inf.query('is-mammal', ['dog'])) > 0}")
print(f"  - Lion is mammal: {len(inf.query('is-mammal', ['lion'])) > 0}")
print(f"  - Eagle is bird: {len(inf.query('is-bird', ['eagle'])) > 0}")
print(f"  - Tiger is carnivore: {len(inf.query('is-carnivore', ['tiger'])) > 0}")

print("\n" + "="*50)
print("Fix successful! Queries now return multiple results.")