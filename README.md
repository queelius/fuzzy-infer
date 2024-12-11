# FuzzyInfer: A Fuzzy Forward-Chaining Production Rule System

**FuzzyInfer** is a Python-based production rule system designed for fuzzy inference. It extends classical forward-chaining systems by incorporating fuzzy logic, allowing the handling of uncertainty and degrees of belief in knowledge representation and reasoning.

## Table of Contents

- [FuzzyInfer: A Fuzzy Forward-Chaining Production Rule System](#fuzzyinfer-a-fuzzy-forward-chaining-production-rule-system)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Key Concepts](#key-concepts)
    - [Beliefs](#beliefs)
    - [Rules](#rules)
    - [Set-Theoretic Predicates](#set-theoretic-predicates)
    - [Fuzzy Inference](#fuzzy-inference)
  - [Architecture](#architecture)
    - [Class Structure](#class-structure)
    - [Methods Overview](#methods-overview)
  - [Usage](#usage)
    - [Initializing the System](#initializing-the-system)
    - [Adding Facts and Rules](#adding-facts-and-rules)
    - [Running Inference](#running-inference)
    - [Asking Questions](#asking-questions)
  - [Design Decisions](#design-decisions)
  - [Future Plans](#future-plans)
  - [Example](#example)
  - [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [Appendix](#appendix)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Testing](#testing)
- [Conclusion](#conclusion)

## Introduction

FuzzyInfer leverages fuzzy logic to manage and infer knowledge that is inherently uncertain or imprecise. Unlike classical Boolean logic, which deals with binary true/false values, fuzzy logic allows for degrees of truth, enabling more nuanced reasoning similar to human decision-making processes.

This system is particularly useful in domains where information is incomplete or ambiguous, such as natural language processing, control systems, and decision support systems.

## Key Concepts

### Beliefs

**Beliefs** represent the fuzzy or uncertain knowledge about the world within the knowledge base (KB). Each belief encodes a predicate, its arguments, and a degree of membership indicating the truth value.

**Example:**
```python
{'pred': 'is-male', 'args': ['sam'], 'deg': 1.0}
{'pred': 'is-person', 'args': ['sam'], 'deg': 1.0}
```

These beliefs assert that Sam is male and a person with full certainty (`deg`: 1.0).

### Rules

**Rules** define relationships between facts (beliefs) and dictate how new facts can be inferred from existing ones. Each rule consists of two parts:

- **Conditions:** A set of predicates that must be satisfied for the rule to fire. Each condition can include a degree-of-belief threshold.
  
- **Actions:** Operations to perform when conditions are met, typically resulting in adding new facts to the KB with specified degrees of membership.

**Example Rule:**
```python
{
    'cond': [
        {
            'pred': 'is-football',
            'args': ['?x'],
            'deg': '?d',
            'deg-pred': ['>', '?d', 0.5]
        }
    ],
    'actions': [
        {
            'action': 'add',
            'fact': {
                'pred': 'is-round',
                'args': ['?x'],
                'deg': ['*', 0.7, '?d']
            }
        }
    ]
}
```
This rule states that if something is a football with a degree of membership greater than 0.5, then it is inferred to be round with a degree of membership multiplied by 0.7.

### Set-Theoretic Predicates

Set-theoretic predicates allow for complex logical conditions within rules, including `and`, `or`, and `not` operations. By default, multiple conditions within a rule are combined using logical `and`, but this behavior can be explicitly controlled.

**Examples:**

- **OR Condition:**
  ```python
  {
      'cond': [
          {
              'or': [
                  {'pred': 'is-mammal', 'args': ['?x']},
                  {'pred': 'has-hair', 'args': ['?x']}
              ]
          }
      ],
      'actions': [
          {
              'action': 'add',
              'fact': {
                  'pred': 'is-hairy-animal',
                  'args': ['?x']
              }
          }
      ]
  }
  ```

- **NOT Condition:**
  ```python
  {
      'cond': [
          {'pred': 'is-mammal', 'args': ['?x']},
          {'not': {'pred': 'has-hair', 'args': ['?x']}}
      ],
      'actions': [
          {
              'action': 'add',
              'fact': {
                  'pred': 'is-shaven-animal',
                  'args': ['?x']
              }
          }
      ]
  }
  ```

### Fuzzy Inference

**Fuzzy Inference** is the core process where the system applies rules to fuzzy facts to derive new facts, managing degrees of uncertainty. The inference operates by:

1. **Rule Evaluation:** For each rule, check if the current facts satisfy the rule's conditions.
2. **Action Execution:** If conditions are met, perform the specified actions to update the KB.
3. **Iteration:** Repeat the process until no new facts are inferred.

The system uses a brute-force forward-chaining approach for simplicity and ease of understanding, making it suitable for educational purposes despite being less efficient than optimized algorithms like Rete.

## Architecture

### Class Structure

```python
class FuzzyInfer:
    """
    Production rule system for fuzzy inference.
    """
    def __init__(self):
        self.facts = list()
        self.rules = list()
    
    def add_rule(self, rule: Dict):
        pass
    
    def add_rules(self, rules: List) -> None:
        pass
    
    def add_fact(self, fact):
        pass
    
    def add_facts(self, facts):
        pass
    
    def add_facts_from_dict(self, facts):
        pass
    
    def act(self, actions) -> None:
        pass
    
    def ask(self, question) -> Dict:
        pass
    
    def satisfies(self, conds) -> bool:
        pass
    
    def run(self):
        pass
    
    def apply_rule(self, rule, facts):
        pass
```

### Methods Overview

- **Initialization:**
  - `__init__`: Sets up empty lists for facts and rules.

- **Adding Rules:**
  - `add_rule`: Adds a single rule to the system.
  - `add_rules`: Adds multiple rules at once.

- **Adding Facts:**
  - `add_fact`: Adds a single fact to the KB.
  - `add_facts`: Adds multiple facts.
  - `add_facts_from_dict`: Adds facts from a dictionary format.

- **Inference Mechanism:**
  - `run`: Executes the inference process by applying rules until no new facts are generated.
  - `satisfies`: Checks if current facts satisfy the conditions of a rule.
  - `act`: Executes the actions specified by a rule when its conditions are met.
  - `apply_rule`: Helper method to apply a rule's actions to the facts.

- **Querying:**
  - `ask`: Allows users to query the KB to retrieve inferred facts based on specified conditions.

## Usage

### Initializing the System

First, instantiate the `FuzzyInfer` class:

```python
from fuzzy_infer import FuzzyInfer

inf = FuzzyInfer()
```

### Adding Facts and Rules

**Adding Facts:**

```python
# Adding a single fact
inf.add_fact({'pred': 'is-male', 'args': ['sam'], 'deg': 1.0})

# Adding multiple facts
facts = [
    {'pred': 'is-person', 'args': ['sam'], 'deg': 1.0},
    {'pred': 'is-zebra', 'args': ['sam'], 'deg': 0.8}
]
inf.add_facts(facts)
```

**Adding Rules:**

```python
# Adding a single rule
rule = {
    'cond': [
        {
            'pred': 'is-zebra',
            'args': ['?x'],
            'deg': '?d',
            'deg-pred': ['>', '?d', 0.5]
        }
    ],
    'actions': [
        {
            'action': 'add',
            'fact': {
                'pred': 'has-stripes',
                'args': ['?x'],
                'deg': ['*', 0.9, '?d']
            }
        }
    ]
}
inf.add_rule(rule)

# Adding multiple rules
rules = [rule1, rule2, rule3]
inf.add_rules(rules)
```

### Running Inference

Execute the inference process to apply all applicable rules and update the KB with inferred facts:

```python
inf.run()
```

### Asking Questions

Query the KB to retrieve facts that satisfy certain conditions.

**Example 1: Simple Query**

```python
# Ask if Sam is a zebra
answer = inf.ask([["is-zebra", ["sam"]]])
print(answer)
```

**Example 2: Complex Query with Variables**

```python
# Ask for dwarven wizards that know conjuration and are married
answer = inf.ask(
    ["uses-conjuration", ["?x"]],
    ["is-dwarven", ["?x"]],  
    ["is-wizard", ["?x"]],
    ["or", ["is-married", ["?x", "?y"]],
           ["is-married", ["?y", "?x"]]]
)
print(answer)
```

The system will return a list of facts that satisfy the query conditions, considering the degrees of membership.

## Design Decisions

- **Fuzzy Logic Integration:** Unlike traditional Boolean systems, FuzzyInfer incorporates degrees of belief, enabling more flexible and realistic knowledge representation.

- **Brute-Force Forward-Chaining:** Chosen for simplicity and ease of understanding, making it suitable for educational purposes. Although less efficient than algorithms like Rete, it facilitates easier debugging and extension.

- **Extensible Architecture:** The system is designed to be easily extendable, allowing for future enhancements such as integrating with large language models (LLMs) for dynamic rule generation.

- **Readable Data Structures:** Rules and facts are represented as dictionaries, making them easy to construct, parse, and manipulate programmatically.

## Future Plans

- **LLM Integration:** Incorporate large language models to dynamically infer new rules and facts based on existing knowledge, enabling a form of meta-learning where the system evolves its knowledge base autonomously.

- **Optimization:** Explore more efficient inference algorithms to enhance performance, potentially integrating aspects of the Rete algorithm adapted for fuzzy logic.

- **User Interface:** Develop a user-friendly interface or API for interacting with the inference system, facilitating broader adoption and ease of use.

- **Advanced Fuzzy Operations:** Implement more sophisticated fuzzy operations and membership functions to handle a wider range of uncertainty and belief representations.

## Example

Here's a complete example demonstrating how to use FuzzyInfer:

```python
from fuzzy_infer import FuzzyInfer

# Initialize the inference system
inf = FuzzyInfer()

# Add facts
inf.add_facts([
    {'pred': 'is-person', 'args': ['sam'], 'deg': 1.0},
    {'pred': 'is-male', 'args': ['sam'], 'deg': 1.0},
    {'pred': 'is-zebra', 'args': ['sam'], 'deg': 0.8}
])

# Add rules
rules = [
    {
        'cond': [
            {
                'pred': 'is-zebra',
                'args': ['?x'],
                'deg': '?d',
                'deg-pred': ['>', '?d', 0.5]
            }
        ],
        'actions': [
            {
                'action': 'add',
                'fact': {
                    'pred': 'has-stripes',
                    'args': ['?x'],
                    'deg': ['*', 0.9, '?d']
                }
            }
        ]
    },
    {
        'cond': [
            {
                'pred': 'is-person',
                'args': ['?x'],
                'deg': '?d',
                'deg-pred': ['>', '?d', 0.9]
            }
        ],
        'actions': [
            {
                'action': 'add',
                'fact': {
                    'pred': 'is-male',
                    'args': ['?x'],
                    'deg': ['*', 0.5, '?d']
                }
            }
        ]
    }
]
inf.add_rules(rules)

# Run inference
inf.run()

# Ask a question
answer = inf.ask([["has-stripes", ["sam"]]])
print("Does Sam have stripes?", answer)
```

**Output:**
```
Does Sam have stripes? [{'pred': 'has-stripes', 'args': ['sam'], 'deg': 0.72}]
```

In this example:

1. **Facts Added:**
   - Sam is a person (`deg`: 1.0).
   - Sam is male (`deg`: 1.0).
   - Sam is a zebra (`deg`: 0.8).

2. **Rules Defined:**
   - If something is a zebra with `deg` > 0.5, then it has stripes with `deg` multiplied by 0.9.
   - If something is a person with `deg` > 0.9, then it is male with `deg` multiplied by 0.5.

3. **Inference:**
   - Applying the first rule infers that Sam has stripes with `deg` = 0.8 * 0.9 = 0.72.
   - The second rule does not alter the existing `is-male` fact since Sam's `deg` as a person is 1.0, but the existing `is-male` fact already has `deg` = 1.0, which is higher than 0.5.

4. **Query:**
   - Asking if Sam has stripes returns the inferred fact with `deg` = 0.72.

## License

This project is licensed under the [MIT License](LICENSE).

# Acknowledgments

FuzzyInfer is inspired by classical production rule systems and fuzzy logic principles, aiming to provide an accessible platform for exploring and implementing fuzzy inference mechanisms.

# Contact

For questions, suggestions, or contributions, please open an issue or submit a pull request on the [GitHub repository](https://github.com/yourusername/fuzzyinfer).

# Contributing

Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) before submitting.

# Disclaimer

This is a simplified implementation intended for educational purposes. For production-grade systems, consider more optimized and feature-rich libraries.

# Appendix

## Dependencies

- Python 3.6+
- No external libraries required.

## Installation

Clone the repository and install any necessary dependencies:

```bash
git clone https://github.com/yourusername/fuzzyinfer.git
cd fuzzyinfer
pip install -r requirements.txt
```

*Note: As there are no external dependencies, the `requirements.txt` may be empty or omitted.*

## Testing

Run the provided example or write custom tests to ensure the system behaves as expected.

```bash
python example.py
```

# Conclusion

FuzzyInfer offers a straightforward yet powerful framework for implementing fuzzy inference systems. Its design prioritizes simplicity and extensibility, making it an excellent tool for both learning and prototyping fuzzy logic applications.

Feel free to explore, experiment, and contribute to enhance its capabilities!