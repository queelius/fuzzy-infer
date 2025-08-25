# FuzzyInfer API Reference

## Core Module (`fuzzy_infer.core`)

### FuzzyInfer

The main inference engine class.

```python
class FuzzyInfer:
    """Forward-chaining fuzzy inference engine."""
    
    def __init__(self) -> None:
        """Initialize empty knowledge base."""
```

#### Methods

##### add_fact
```python
def add_fact(self, fact: Union[Fact, Dict[str, Any]]) -> "FuzzyInfer":
    """
    Add a fact to the knowledge base.
    
    Args:
        fact: Fact object or dict with 'pred', 'args', 'deg' keys
        
    Returns:
        Self for method chaining
        
    Example:
        inf.add_fact(Fact("is-tall", ["john"], 0.8))
        inf.add_fact({"pred": "is-tall", "args": ["john"], "deg": 0.8})
    """
```

##### add_rule
```python
def add_rule(self, rule: Union[Rule, Dict[str, Any]]) -> "FuzzyInfer":
    """
    Add a rule to the rule base.
    
    Args:
        rule: Rule object or dict representation
        
    Returns:
        Self for method chaining
    """
```

##### run
```python
def run(self, max_iterations: int = 100) -> "FuzzyInfer":
    """
    Execute forward-chaining inference.
    
    Args:
        max_iterations: Maximum iterations (prevents infinite loops)
        
    Returns:
        Self for method chaining
        
    Raises:
        InferenceError: If max iterations exceeded
    """
```

##### query
```python
def query(self, predicate: str, args: Optional[List[str]] = None) -> List[Fact]:
    """
    Query facts matching a pattern.
    
    Args:
        predicate: Predicate to match
        args: Optional argument pattern (None matches any)
        
    Returns:
        List of matching facts
        
    Example:
        inf.query("is-mammal")  # All mammals
        inf.query("is-mammal", ["dog"])  # Specific query
    """
```

##### clear
```python
def clear(self) -> "FuzzyInfer":
    """Clear all facts and rules."""
```

##### get_facts / get_rules
```python
def get_facts(self) -> List[Fact]:
    """Return all facts in the knowledge base."""
    
def get_rules(self) -> List[Rule]:
    """Return all rules in the rule base."""
```

---

## Models Module (`fuzzy_infer.models`)

### Fact
```python
@dataclass(frozen=True)
class Fact:
    """
    Immutable fact with fuzzy degree.
    
    Attributes:
        predicate: Fact predicate/relation
        args: Fact arguments
        degree: Degree of belief [0.0, 1.0]
    """
    predicate: str
    args: List[str]
    degree: float = 1.0
    
    def matches_pattern(self, pattern: "Fact", 
                        bindings: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
        """Check if fact matches pattern with variable bindings."""
```

### Rule
```python
@dataclass
class Rule:
    """
    Production rule with conditions and actions.
    
    Attributes:
        conditions: List of conditions to match
        actions: List of actions to execute
        name: Optional rule name
        description: Optional description
        priority: Execution priority (higher first)
    """
    conditions: List[Union[Condition, Dict]]
    actions: List[Union[Action, Dict]]
    name: Optional[str] = None
    description: Optional[str] = None
    priority: int = 0
```

### Condition
```python
@dataclass
class Condition:
    """
    Rule condition with optional degree constraint.
    
    Attributes:
        predicate: Condition predicate
        args: Arguments (can include variables like ?x)
        degree_var: Variable to bind degree to
        degree_constraint: Constraint on degree [op, val1, val2]
        or_conditions: Alternative conditions (OR)
        and_conditions: Conjunctive conditions (AND)
        negated: Whether condition is negated
    """
```

### Action
```python
@dataclass
class Action:
    """
    Rule action to modify knowledge base.
    
    Attributes:
        action_type: 'add', 'modify', or 'retract'
        fact: Fact template with variables
    """
```

### RuleBuilder
```python
class RuleBuilder:
    """
    Fluent API for rule construction.
    
    Example:
        rule = (
            RuleBuilder("my-rule")
            .when("is-bird", ["?x"])
            .when("has-wings", ["?x"], min_degree=0.8)
            .then_add("can-fly", ["?x"], degree=0.9)
            .with_priority(10)
            .build()
        )
    """
    
    def when(self, predicate: str, args: List[str], 
             min_degree: Optional[float] = None) -> "RuleBuilder":
        """Add a condition."""
    
    def then_add(self, predicate: str, args: List[str], 
                 degree: Union[float, List] = 1.0) -> "RuleBuilder":
        """Add an action to add a fact."""
    
    def with_priority(self, priority: int) -> "RuleBuilder":
        """Set rule priority."""
    
    def build(self) -> Rule:
        """Build the rule."""
```

---

## Fuzzy Operations Module (`fuzzy_infer.fuzzy_ops`)

### T-Norms (AND Operations)

```python
class TNorm(Protocol):
    """Protocol for fuzzy AND operations."""
    def __call__(self, a: float, b: float) -> float: ...

# Available T-Norms
MIN_TNORM = MinimumTNorm()           # min(a, b)
PRODUCT_TNORM = ProductTNorm()       # a * b
LUKASIEWICZ_TNORM = LukasiewiczTNorm()  # max(0, a + b - 1)
```

### T-Conorms (OR Operations)

```python
class TConorm(Protocol):
    """Protocol for fuzzy OR operations."""
    def __call__(self, a: float, b: float) -> float: ...

# Available T-Conorms
MAX_TCONORM = MaximumTConorm()       # max(a, b)
PROB_SUM_TCONORM = ProbabilisticSumTConorm()  # a + b - a*b
BOUNDED_SUM_TCONORM = BoundedSumTConorm()     # min(1, a + b)
```

### Negation Operations

```python
class Negation(Protocol):
    """Protocol for fuzzy NOT operations."""
    def __call__(self, a: float) -> float: ...

# Available Negations
STANDARD_NEGATION = StandardNegation()   # 1 - a
SUGENO_NEGATION = SugenoNegation(λ)      # (1 - a) / (1 + λ * a)
YAGER_NEGATION = YagerNegation(w)        # (1 - a^w)^(1/w)
```

### Hedges (Modifiers)

```python
class Hedge(Protocol):
    """Protocol for linguistic hedges."""
    def __call__(self, a: float) -> float: ...

# Available Hedges
VERY = PowerHedge(2.0)          # a^2 (concentration)
SOMEWHAT = PowerHedge(0.5)      # a^0.5 (dilation)
EXTREMELY = PowerHedge(3.0)     # a^3
```

---

## Merge Module (`fuzzy_infer.merge`)

### KnowledgeBaseMerger

```python
class KnowledgeBaseMerger:
    """
    Merge multiple knowledge bases with conflict detection.
    
    Args:
        threshold: Degree difference threshold for conflicts (0.5)
    """
    
    def merge(self, kb1: FuzzyInfer, kb2: FuzzyInfer,
              strategy: MergeStrategy = MergeStrategy.UNION,
              weights: Optional[Tuple[float, float]] = None,
              auto_resolve: bool = False) -> FuzzyInfer:
        """
        Merge two knowledge bases.
        
        Args:
            kb1: First knowledge base
            kb2: Second knowledge base
            strategy: Merge strategy to use
            weights: Weights for weighted merge
            auto_resolve: Auto-resolve conflicts (SMART mode)
            
        Returns:
            Merged knowledge base
        """
    
    def get_conflict_report(self) -> str:
        """Generate human-readable conflict report."""
```

### MergeStrategy

```python
class MergeStrategy(Enum):
    """Available merge strategies."""
    UNION = "union"           # Combine all, max degree for duplicates
    OVERRIDE = "override"     # KB2 takes precedence
    COMPLEMENT = "complement" # Only add new items
    WEIGHTED = "weighted"     # Weighted average
    SMART = "smart"          # Intelligent conflict resolution
```

### Conflict

```python
@dataclass
class Conflict:
    """
    Detected conflict between knowledge bases.
    
    Attributes:
        type: Conflict type
        severity: Severity score [0.0, 1.0]
        kb1_item: Item from first KB
        kb2_item: Item from second KB
        description: Human-readable description
        suggested_resolution: Resolution suggestion
    """
```

---

## Serialization Module (`fuzzy_infer.serialization`)

### FuzzyInferSerializer

```python
class FuzzyInferSerializer:
    """Handle knowledge base I/O."""
    
    @staticmethod
    def to_dict(inf: FuzzyInfer) -> Dict[str, Any]:
        """Convert to dictionary representation."""
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> FuzzyInfer:
        """Create from dictionary representation."""
    
    @staticmethod
    def save_to_file(inf: FuzzyInfer, filepath: Union[str, Path]) -> None:
        """Save to JSON or YAML file."""
    
    @staticmethod
    def load_from_file(filepath: Union[str, Path]) -> FuzzyInfer:
        """Load from JSON or YAML file."""
```

---

## CLI Module (`fuzzy_infer.cli`)

### Commands

```python
@app.command()
def interactive():
    """Start interactive REPL session."""

@app.command()
def run(knowledge_base: Path, output: Optional[Path] = None):
    """Run inference on a knowledge base file."""

@app.command()
def validate(knowledge_base: Path):
    """Validate a knowledge base file."""

@app.command()
def merge(kb1: Path, kb2: Path, 
         strategy: str = "union",
         output: Optional[Path] = None):
    """Merge two knowledge bases."""
```

---

## Exceptions Module (`fuzzy_infer.exceptions`)

```python
class FuzzyInferError(Exception):
    """Base exception for FuzzyInfer."""

class ValidationError(FuzzyInferError):
    """Invalid data or constraint violation."""

class InferenceError(FuzzyInferError):
    """Error during inference execution."""

class SerializationError(FuzzyInferError):
    """Error during serialization/deserialization."""

class MergeError(FuzzyInferError):
    """Error during knowledge base merging."""
```

---

## Usage Examples

### Basic Inference
```python
from fuzzy_infer import FuzzyInfer, Fact, Rule

inf = FuzzyInfer()
inf.add_fact(Fact("temperature", ["room"], 0.8))
inf.add_rule(hot_rule)
inf.run()
results = inf.query("is-hot")
```

### With Builder Pattern
```python
from fuzzy_infer.models import RuleBuilder

rule = (
    RuleBuilder("temperature-rule")
    .when("temperature", ["?x"], min_degree=0.7)
    .then_add("is-hot", ["?x"], degree=0.9)
    .build()
)
```

### Knowledge Base Merging
```python
from fuzzy_infer.merge import KnowledgeBaseMerger, MergeStrategy

merger = KnowledgeBaseMerger()
merged = merger.merge(kb1, kb2, MergeStrategy.SMART)
print(merger.get_conflict_report())
```

### Serialization
```python
from fuzzy_infer.serialization import FuzzyInferSerializer

# Save
FuzzyInferSerializer.save_to_file(inf, "knowledge.json")

# Load
inf = FuzzyInferSerializer.load_from_file("knowledge.yaml")
```