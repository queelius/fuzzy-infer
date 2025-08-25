#!/usr/bin/env python3
"""Test knowledge base merging with conflict detection."""

from fuzzy_infer.serialization import FuzzyInferSerializer
from fuzzy_infer.merge import KnowledgeBaseMerger, MergeStrategy

# Load the two conflicting KBs
kb1 = FuzzyInferSerializer.load_from_file("examples/knowledge_bases/animals_kb1.json")
kb2 = FuzzyInferSerializer.load_from_file("examples/knowledge_bases/animals_kb2.json")

print("KB1 Summary:")
print(f"  Facts: {len(kb1.get_facts())}")
print(f"  Rules: {len(kb1.get_rules())}")

print("\nKB2 Summary:")
print(f"  Facts: {len(kb2.get_facts())}")
print(f"  Rules: {len(kb2.get_rules())}")

print("\n" + "="*60)
print("Testing different merge strategies...")
print("="*60)

# Test each merge strategy
strategies = [
    MergeStrategy.UNION,
    MergeStrategy.OVERRIDE,
    MergeStrategy.COMPLEMENT,
    MergeStrategy.WEIGHTED,
    MergeStrategy.SMART
]

for strategy in strategies:
    print(f"\n{strategy.value.upper()} Merge:")
    print("-" * 40)
    
    merger = KnowledgeBaseMerger(threshold=0.5)
    
    if strategy == MergeStrategy.WEIGHTED:
        merged = merger.merge(kb1, kb2, strategy, weights=(0.7, 0.3))
    else:
        merged = merger.merge(kb1, kb2, strategy, auto_resolve=True)
    
    print(f"Result: {len(merged.get_facts())} facts, {len(merged.get_rules())} rules")
    
    # Show conflicts for smart merge
    if strategy == MergeStrategy.SMART and merger.conflicts:
        print("\nConflicts detected:")
        for conflict in merger.conflicts[:3]:
            print(f"  - {conflict.type}: {conflict.description}")
            print(f"    Severity: {conflict.severity:.2f}")
    
    # Show specific merged facts
    if strategy in [MergeStrategy.SMART, MergeStrategy.WEIGHTED]:
        print("\nKey merged facts:")
        for fact in merged.get_facts():
            if fact.predicate == "is-dangerous" and fact.args == ["dog"]:
                print(f"  is-dangerous(dog): {fact.degree:.2f}")
            if fact.predicate == "species" and fact.args[0] == "rover":
                print(f"  species(rover, {fact.args[1]}): {fact.degree:.2f}")

print("\n" + "="*60)
print("Detailed SMART merge conflict report:")
print("="*60)

# Do a detailed smart merge
merger = KnowledgeBaseMerger(threshold=0.3)  # Lower threshold to catch more conflicts
merged = merger.merge(kb1, kb2, MergeStrategy.SMART, auto_resolve=False)

print(merger.get_conflict_report())