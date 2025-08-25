# CLAUDE.md - FuzzyInfer Implementation Guide

This file provides implementation details and design notes for Claude Code when working with the FuzzyInfer codebase.

## 🎯 Project Overview

FuzzyInfer has been transformed from a simple educational prototype (265 lines) into a production-ready package with:
- Full test suite (91.71% coverage)
- Interactive CLI with REPL
- Knowledge base merging with conflict detection
- Modern Python packaging
- Comprehensive examples and documentation

## 🏗️ Architecture & Design

### Core Components

#### 1. **Inference Engine (`core.py`)**
- **Key Fix Applied**: Modified `_match_condition` to collect ALL matching facts instead of just the first
- **Pattern Matching**: Uses `_match_all_conditions` for comprehensive binding collection
- **Fuzzy OR**: Automatically handles duplicate facts by taking maximum degree
- **Priority System**: Rules execute in priority order (higher first)

#### 2. **Data Models (`models.py`)**
- `Fact`: Immutable fact with predicate, args, and degree
- `Rule`: Contains conditions and actions with optional priority
- `Condition`: Supports predicates, variables, degree constraints, and logical operators
- `Action`: Defines operations (add, modify, retract)
- `RuleBuilder`: Fluent API for rule construction

#### 3. **Fuzzy Operations (`fuzzy_ops.py`)**
- T-norms (AND): minimum, product, Lukasiewicz
- T-conorms (OR): maximum, probabilistic sum, bounded sum
- Negation: standard, sugeno, yager
- Hedges: very, somewhat, extremely
- Custom operations via `FuzzyOperation` protocol

#### 4. **Knowledge Base Merging (`merge.py`)**
- **5 Strategies**: UNION, OVERRIDE, COMPLEMENT, WEIGHTED, SMART
- **Conflict Detection**:
  - Fact contradictions (large degree differences)
  - Mutual exclusions (e.g., can't be two species)
  - Rule conflicts (same name, different logic)
  - Subsumption (general vs specific rules)
- **Auto-resolution**: Based on confidence, priority, specificity

#### 5. **CLI/REPL (`cli.py`)**
- **Enhanced Features**:
  - File system navigation (cd, ls, pwd)
  - Command history with arrow keys (via prompt-toolkit)
  - History command
  - Merge command with strategy selection
- **Commands**: facts, rules, query, run, load, save, merge, clear

## 🐛 Key Issues Fixed

### 1. **Multiple Results Bug**
**Problem**: Queries only returned single results
**Root Cause**: `_match_condition` returned after first match
**Solution**: Created `_match_all_conditions` to collect all bindings
```python
# Before: return True, new_bindings, fact.degree
# After: all_matches.append((new_bindings, fact.degree))
```

### 2. **Inference Not Creating Classifications**
**Problem**: Rules weren't classifying all matching entities
**Solution**: Modified `_satisfies_conditions` to use new matching method

## 📝 Important Implementation Notes

### Fact Storage
- Facts stored as dict with key `(predicate, tuple(args))`
- Fuzzy OR handled automatically on duplicate insertion
- Degrees clamped to [0.0, 1.0]

### Rule Execution
1. Rules sorted by priority on insertion
2. All rules checked each iteration (brute force)
3. Inference continues until no new facts generated
4. Actions can add, modify, or retract facts

### Variable Binding
- Variables use `?x` notation
- Bindings propagated through condition matching
- Support for degree variables (`?d`)
- Arithmetic operations on degrees

### Conflict Resolution in Merging
- **Fact conflicts**: Average degrees if close, otherwise use higher
- **Rule conflicts**: Keep higher priority or more specific
- **Mutual exclusions**: Keep both with uncertainty
- **Semantic contradictions**: Flag for review

## 🧪 Testing Strategy

### Coverage Areas
- Core inference engine (forward chaining)
- Fuzzy operations (all T-norms/conorms)
- Pattern matching with variables
- Degree calculations and constraints
- Serialization (JSON/YAML)
- CLI commands
- Knowledge base merging

### Test Files
- `test_core.py`: Inference engine tests
- `test_models.py`: Data model tests
- `test_fuzzy_ops.py`: Fuzzy operation tests
- `test_serialization.py`: I/O tests
- `test_merge.py`: KB merging tests
- `test_cli.py`: CLI functionality tests

## 🚀 Performance Considerations

### Current Limitations
- Brute-force forward chaining (O(n*m) per iteration)
- No indexing of facts or rules
- Full re-evaluation each iteration

### Optimization Opportunities
1. **Rete-like Network**: Build discrimination network
2. **Fact Indexing**: Hash facts by predicate
3. **Incremental Updates**: Track changes between iterations
4. **Lazy Evaluation**: Defer degree calculations

## 📦 Dependencies

### Core Package
- Pure Python (no dependencies)

### Optional Dependencies
- **CLI**: typer, rich, prompt-toolkit
- **Serialization**: pyyaml
- **Development**: pytest, black, ruff, mypy

## 🔧 Common Development Tasks

### Running Tests
```bash
pytest                          # All tests
pytest --cov=fuzzy_infer       # With coverage
pytest -xvs                    # Verbose, stop on failure
```

### Code Quality
```bash
black fuzzy_infer/             # Format code
ruff check fuzzy_infer/        # Lint
mypy fuzzy_infer/              # Type check
```

### Building Package
```bash
pip install -e .               # Development install
python -m build                # Build distributions
```

## 🎓 Educational vs Production

### Educational Aspects Retained
- Clear, readable code structure
- Comprehensive docstrings
- Simple brute-force algorithm
- Extensive examples

### Production Enhancements Added
- Error handling and validation
- Type hints throughout
- Comprehensive test suite
- CLI with professional UX
- Knowledge base merging
- Serialization support

## 🔮 Future Enhancements

### High Priority
1. Backward chaining support
2. Explanation system (why was fact inferred?)
3. Web UI for visualization
4. REST API server mode

### Medium Priority
1. Performance optimizations
2. More fuzzy operations
3. Certainty factor model
4. Temporal reasoning

### Low Priority
1. LLM integration for rule generation
2. Distributed inference
3. Real-time streaming support

## 💡 Design Decisions Explained

### Why Brute Force?
- **Simplicity**: Easy to understand and debug
- **Completeness**: Guarantees all applicable rules fire
- **Flexibility**: Easy to add new features
- **Educational**: Clear algorithmic flow

### Why Fuzzy OR for Duplicates?
- **Standard Practice**: Common in fuzzy systems
- **Intuitive**: Multiple sources increase confidence
- **Monotonic**: Never decreases belief

### Why Pattern Variables?
- **Expressiveness**: Write general rules
- **Reusability**: Same rule applies to many entities
- **Standard**: Common in production systems

## 🚨 Known Issues & Workarounds

### Issue 1: Large Knowledge Bases Slow
**Workaround**: Split into smaller KBs and merge

### Issue 2: No Backward Chaining
**Workaround**: Manually add goal-seeking rules

### Issue 3: No Explanation System
**Workaround**: Enable debug logging to trace inference

## 📊 Metrics & Performance

- **Test Coverage**: 91.71%
- **Inference Speed**: ~1000 facts/second (typical)
- **Memory Usage**: Linear with facts + rules
- **Startup Time**: < 100ms
- **CLI Response**: < 50ms

## 🔄 Workflow Tips

### Adding New Features
1. Write tests first (TDD)
2. Update models if needed
3. Implement in core
4. Add CLI support
5. Update documentation
6. Run full test suite

### Debugging Inference
1. Enable debug logging
2. Use small test cases
3. Trace variable bindings
4. Check degree calculations
5. Verify rule conditions

### Reviewing Merges
1. Check conflict report
2. Verify resolution strategy
3. Test merged KB
4. Compare results

---

*Last Updated: After major refactoring and production-ready enhancements*