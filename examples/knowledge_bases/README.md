# FuzzyInfer Knowledge Base Examples

This directory contains example knowledge bases written in the FuzzyInfer DSL (Domain Specific Language). These can be loaded and executed using the CLI or programmatically.

## File Formats

FuzzyInfer supports both JSON and YAML formats for knowledge bases.

## DSL Structure

### Facts
Facts represent assertions about the world with a degree of certainty (0.0 to 1.0):

```json
{"pred": "predicate-name", "args": ["arg1", "arg2"], "deg": 0.8}
```

### Rules
Rules define inference logic with conditions and actions:

```json
{
  "name": "rule-name",
  "cond": [...],      // Conditions to match
  "actions": [...],   // Actions to execute when conditions match
  "priority": 10      // Optional: Higher priority rules execute first
}
```

### Conditions

#### Simple Condition
```json
{"pred": "is-human", "args": ["?x"]}
```

#### With Degree Variable and Constraint
```json
{
  "pred": "temperature",
  "args": ["?day", "high"],
  "deg": "?temp",
  "deg-pred": [">", "?temp", 0.7]
}
```

#### Logical Operators

**OR:**
```json
{
  "or": [
    {"pred": "has-wings", "args": ["?x"]},
    {"pred": "is-airplane", "args": ["?x"]}
  ]
}
```

**AND:**
```json
{
  "and": [
    {"pred": "is-tall", "args": ["?x"]},
    {"pred": "is-heavy", "args": ["?x"]}
  ]
}
```

**NOT:**
```json
{"not": {"pred": "is-dangerous", "args": ["?x"]}}
```

### Actions

#### Add Fact
```json
{"action": "add", "fact": {"pred": "can-fly", "args": ["?x"], "deg": 0.9}}
```

#### Remove Fact
```json
{"action": "remove", "fact": {"pred": "old-fact", "args": ["?x"]}}
```

#### Modify Fact Degree
```json
{"action": "modify", "fact": {"pred": "belief", "args": ["?x"], "deg": 0.5}}
```

### Degree Calculations

Degrees can be constants or calculated expressions:

- **Constant:** `"deg": 0.8`
- **Variable:** `"deg": "?d"`
- **Multiplication:** `"deg": ["*", "?d", 0.9]`
- **Addition:** `"deg": ["+", "?d1", "?d2"]`
- **Subtraction:** `"deg": ["-", 1.0, "?d"]`
- **Division:** `"deg": ["/", "?d", 2.0]`
- **Minimum:** `"deg": ["min", "?d1", "?d2", "?d3"]`
- **Maximum:** `"deg": ["max", "?d1", "?d2"]`

## Running Examples

### Using the CLI

```bash
# Run inference on a knowledge base
fuzzy-infer run animal_classification.json

# Query specific facts after inference
fuzzy-infer run weather_prediction.yaml --query "precipitation"

# Save results to a new file
fuzzy-infer run medical_diagnosis.json --output results.json

# Validate a knowledge base
fuzzy-infer validate animal_classification.json
```

### Interactive Mode

```bash
# Start interactive session
fuzzy-infer interactive

# In the session:
fuzzy> load animal_classification.json
fuzzy> run
fuzzy> query is-mammal
fuzzy> facts
```

### Programmatically

```python
from fuzzy_infer.serialization import FuzzyInferSerializer

# Load and run
inf = FuzzyInferSerializer.load_from_file("animal_classification.json")
inf.run()
results = inf.query("is-carnivore")

# Save results
FuzzyInferSerializer.save_to_file(inf, "output.yaml")
```

## Example Knowledge Bases

### animal_classification.json
A classical animal classification system using physical characteristics to determine species and categories.

### weather_prediction.yaml
A fuzzy weather prediction system that uses multiple indicators to predict rain and make recommendations.

### medical_diagnosis.json
A medical diagnosis assistant that considers symptoms, test results, and patient history to suggest possible diagnoses and treatments.