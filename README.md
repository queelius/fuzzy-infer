# FuzzyInfer: A Production-Ready Fuzzy Logic Inference System

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-91.71%25-brightgreen.svg)](tests/)

**FuzzyInfer** is a production-ready Python package for fuzzy logic inference using forward-chaining production rules. It extends classical rule-based systems by incorporating degrees of belief, enabling sophisticated reasoning under uncertainty.

## 🚀 Features

- **Fuzzy Logic Integration**: Handle uncertainty with degrees of belief (0.0 to 1.0)
- **Forward-Chaining Inference**: Automatic derivation of new facts from rules
- **Interactive CLI/REPL**: Powerful command-line interface with file system navigation
- **Knowledge Base Merging**: 5 intelligent merge strategies with conflict detection
- **Multiple Serialization Formats**: JSON and YAML support
- **Comprehensive API**: Fluent interface and builder patterns
- **Production Ready**: 91.71% test coverage, type hints, error handling

## 📦 Installation

### From PyPI (when published)
```bash
pip install fuzzy-infer
```

### From Source
```bash
git clone https://github.com/queelius/fuzzy-infer.git
cd fuzzy-infer
pip install -e .

# With CLI support
pip install -e ".[cli]"

# For development
pip install -e ".[dev]"
```

## 🎯 Quick Start

### Basic Usage

```python
from fuzzy_infer import FuzzyInfer, Fact, Rule

# Create inference engine
inf = FuzzyInfer()

# Add facts with degrees of belief
inf.add_fact(Fact("is-bird", ["tweety"], 0.9))
inf.add_fact(Fact("has-wings", ["tweety"], 1.0))

# Add rules
rule = Rule(
    name="birds-fly",
    conditions=[{"pred": "is-bird", "args": ["?x"]}],
    actions=[{"action": "add", "fact": {"pred": "can-fly", "args": ["?x"], "deg": 0.8}}]
)
inf.add_rule(rule)

# Run inference
inf.run()

# Query results
results = inf.query("can-fly", ["tweety"])
print(results)  # [Fact(predicate='can-fly', args=['tweety'], degree=0.72)]
```

### Interactive CLI

```bash
# Start interactive session
fuzzy-infer interactive

# In the REPL:
> load examples/knowledge_bases/animal_classification.json
> run
> query is-mammal
> help
```

## 🧠 Core Concepts

### Facts (Beliefs)

Facts represent knowledge with uncertainty:

```python
Fact("is-tall", ["john"], 0.8)  # John is tall with 80% certainty
Fact("temperature", ["room", "hot"], 0.6)  # Room temperature is hot with 60% certainty
```

### Rules

Rules define relationships and inference patterns:

```python
{
    "name": "mammals-give-milk",
    "conditions": [
        {"pred": "is-mammal", "args": ["?x"], "deg": "?d", "deg-pred": [">", "?d", 0.7]}
    ],
    "actions": [
        {"action": "add", "fact": {"pred": "gives-milk", "args": ["?x"], "deg": ["*", "?d", 0.9]}}
    ]
}
```

### Degree Operations

- **Fuzzy OR**: Maximum degree for duplicate facts
- **Fuzzy AND**: Minimum degree across conditions
- **Arithmetic**: `["*", 0.8, "?d"]`, `["+", "?d1", "?d2"]`, `["min", "?d1", "?d2"]`

## 🔧 Advanced Features

### Knowledge Base Merging

Merge multiple knowledge bases with intelligent conflict resolution:

```python
from fuzzy_infer.merge import KnowledgeBaseMerger, MergeStrategy

merger = KnowledgeBaseMerger(threshold=0.5)

# Smart merge with conflict detection
merged = merger.merge(kb1, kb2, MergeStrategy.SMART, auto_resolve=True)

# Get conflict report
print(merger.get_conflict_report())
```

**Available Strategies:**
- `UNION`: Combine all facts/rules (default)
- `OVERRIDE`: Second KB takes precedence
- `COMPLEMENT`: Only add new items
- `WEIGHTED`: Weighted average of degrees
- `SMART`: Intelligent conflict detection and resolution

### Fluent API

```python
result = (
    FuzzyInfer()
    .add_fact(Fact("has-hair", ["dog"], 1.0))
    .add_rule(mammal_rule)
    .run()
    .query("is-mammal")
)
```

### Rule Builder DSL

```python
from fuzzy_infer.models import RuleBuilder

rule = (
    RuleBuilder("carnivore-rule")
    .when("eats-meat", ["?x"])
    .when("has-teeth", ["?x"], min_degree=0.5)
    .then_add("is-carnivore", ["?x"], degree=0.9)
    .with_priority(10)
    .build()
)
```

## 🖥️ CLI Commands

The interactive REPL provides powerful commands:

### Facts & Rules
- `fact <predicate> <args...> [degree]` - Add a fact
- `facts` - List all facts
- `query <predicate> [args...]` - Query facts
- `rule <json>` - Add rule in JSON format
- `rules` - List all rules

### Inference
- `run` - Execute forward-chaining inference
- `clear` - Clear all facts and rules

### File Operations
- `load <file>` - Load knowledge base (JSON/YAML)
- `save <file>` - Save current knowledge base
- `merge <file> [strategy]` - Merge another KB

### File System Navigation
- `pwd` - Show current directory
- `cd <path>` - Change directory
- `ls [path]` - List directory contents

### Session
- `history` - Show command history (with arrow key support)
- `help` - Show available commands
- `exit` - Exit the session

## 📊 Examples

### Animal Classification

```python
# Load comprehensive animal knowledge base
inf = FuzzyInferSerializer.load_from_file("examples/animal_classification.json")
inf.run()

# Query all mammals
mammals = inf.query("is-mammal")  # Returns 8 animals

# Query specific animal
inf.query("is-mammal", ["lion"])  # Returns fact with degree 1.0
```

### Weather Prediction

```python
# Fuzzy weather reasoning
inf.add_fact(Fact("cloud-cover", ["today"], 0.8))
inf.add_fact(Fact("humidity", ["today"], 0.7))

# Rule: High clouds + humidity → rain
rule = Rule(
    conditions=[
        {"pred": "cloud-cover", "args": ["?day"], "deg": "?c", "deg-pred": [">", "?c", 0.6]},
        {"pred": "humidity", "args": ["?day"], "deg": "?h", "deg-pred": [">", "?h", 0.6]}
    ],
    actions=[
        {"action": "add", "fact": {"pred": "will-rain", "args": ["?day"], 
                                   "deg": ["*", ["min", "?c", "?h"], 0.9]}}
    ]
)
```

### Medical Diagnosis

```python
# Symptom-based diagnosis with uncertainty
inf.add_fact(Fact("has-symptom", ["patient1", "fever"], 0.9))
inf.add_fact(Fact("has-symptom", ["patient1", "cough"], 0.7))

# Rules infer possible conditions with confidence levels
```

## 🏗️ Architecture

### Project Structure
```
fuzzy-infer/
├── fuzzy_infer/
│   ├── __init__.py        # Package exports
│   ├── core.py            # Main inference engine
│   ├── models.py          # Fact, Rule, Condition classes
│   ├── fuzzy_ops.py       # Fuzzy logic operations
│   ├── merge.py           # KB merging strategies
│   ├── serialization.py   # JSON/YAML I/O
│   ├── cli.py             # Interactive CLI/REPL
│   └── exceptions.py      # Custom exceptions
├── examples/
│   ├── knowledge_bases/   # Example KBs (animals, weather, medical)
│   └── *.py               # Usage examples
├── tests/                 # Comprehensive test suite
└── pyproject.toml         # Modern Python packaging
```

### Key Design Decisions

1. **Multiple Result Support**: Fixed inference engine properly returns ALL matching facts
2. **Fuzzy OR Semantics**: Duplicate facts automatically use maximum degree
3. **Conflict Resolution**: Smart merging detects and resolves semantic conflicts
4. **Priority-Based Rules**: Rules execute in priority order
5. **Pattern Variables**: Support for `?x` style variables in rules
6. **Extensible Operations**: Custom degree calculations and constraints

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=fuzzy_infer --cov-report=html

# Run specific test
pytest tests/test_core.py::test_fuzzy_or

# Current coverage: 91.71%
```

## 📚 Documentation

- [API Reference](docs/api.md) - Complete API documentation
- [Tutorial](docs/tutorial.md) - Step-by-step guide
- [Examples](examples/) - Working code examples
- [Knowledge Bases](examples/knowledge_bases/) - Sample KBs

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Inspired by CLIPS, Jess, and Drools rule engines
- Fuzzy logic principles from Zadeh's fuzzy set theory
- Built with modern Python best practices

## 📮 Contact

- GitHub: [@queelius](https://github.com/queelius)
- Issues: [GitHub Issues](https://github.com/queelius/fuzzy-infer/issues)

## 🚧 Roadmap

- [ ] Backward chaining support
- [ ] Explanation system for inference chains
- [ ] Web UI for knowledge base visualization
- [ ] REST API server mode
- [ ] Performance optimizations (Rete-like algorithm)
- [ ] LLM integration for rule generation
- [ ] More fuzzy operations (hedges, custom membership functions)

---

*FuzzyInfer - Reasoning with Uncertainty*