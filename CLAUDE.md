# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

FuzzyInfer is a Python-based fuzzy logic production rule system implementing forward-chaining inference with degrees of belief. It's designed for educational purposes with a focus on simplicity and clarity over performance.

## Project Structure

```
fuzzy-infer/
├── fuzzy-infer/
│   └── infer.py          # Single module containing FuzzyInfer class (265 lines)
├── examples/
│   ├── example.py        # Python rule format example
│   └── winston.py        # LISP-style rule format example
├── README.md             # Comprehensive documentation
└── LICENSE              # MIT License
```

## Core Architecture

### Main Class: `FuzzyInfer`

Single class design in `fuzzy-infer/infer.py` with key methods:
- `add_fact(fact)` / `add_facts(facts)` - Add fuzzy facts to knowledge base
- `add_rule(rule)` / `add_rules(rules)` - Add production rules
- `run()` - Execute forward-chaining inference
- `ask(question)` - Query the knowledge base
- `satisfies(conds)` - Check if conditions are met
- `act(actions)` - Execute rule actions

### Data Structures

**Facts (Beliefs):**
```python
{'pred': 'is-zebra', 'args': ['sam'], 'deg': 0.8}  # Fuzzy fact with degree
```

**Rules:**
```python
{
    'cond': [{'pred': 'is-zebra', 'args': ['?x'], 'deg': '?d', 'deg-pred': ['>', '?d', 0.5]}],
    'actions': [{'action': 'add', 'fact': {'pred': 'has-stripes', 'args': ['?x'], 'deg': ['*', 0.9, '?d']}}]
}
```

## Current Development Status

**Working:**
- Core fuzzy inference engine
- Examples demonstrating usage
- Comprehensive documentation

**Missing Infrastructure:**
- No test suite or testing framework
- Not pip-installable (no setup.py/pyproject.toml)
- No linting, formatting, or type checking setup
- No CI/CD pipeline
- No requirements.txt (pure Python, no dependencies)

## Development Commands

### Running Examples
```bash
# Run examples (requires manual path setup)
cd examples
python3 -c "import sys; sys.path.append('../fuzzy-infer'); exec(open('example.py').read())"

# Or modify examples to include path
python3 examples/example.py  # After adding sys.path manipulation
```

### Importing the Module
```python
import sys
sys.path.append('./fuzzy-infer')
from infer import FuzzyInfer
```

## Key Implementation Details

1. **Brute-force forward-chaining** - Intentionally simple for educational purposes
2. **Fuzzy logic operations** - Supports degrees of belief (0.0 to 1.0)
3. **Set-theoretic predicates** - Supports `and`, `or`, `not` in rule conditions
4. **Variable binding** - Uses `?x`, `?y` style variables in rules
5. **Dynamic degree calculation** - Supports arithmetic operations on degrees

## Future Development Notes

Per README, planned enhancements include:
- LLM integration for dynamic rule generation
- Performance optimization (possibly Rete algorithm adaptation)
- User interface/API development
- Advanced fuzzy operations

## Important Considerations

1. **Educational codebase** - Prioritizes clarity over performance
2. **Single-file implementation** - All logic in one 265-line file
3. **No external dependencies** - Pure Python implementation
4. **Manual installation** - Requires sys.path manipulation to import

When adding features or tests, maintain the educational focus and clear, simple implementation style.