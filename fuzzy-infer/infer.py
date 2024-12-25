from typing import List, Dict


class FuzzyInfer:
    """
    Production rule system for fuzzy inference. The system is based on the
    following concepts:

    - Beliefs: Beliefs encode the fuzzy or uncertain knowledge about the world.
      For example, 
        - {'pred': 'is-male', 'args': ['sam'], 'deg': 1.0}
        - {'pred': 'is-person', 'args': ['sam'], 'deg': 1.0}

      These two beliefs or facts would be in the knowledge base (KB).

    - Rules: Rules are statements that define relationships between facts. For
        example, "If an animal has hair, then it is a mammal" is a rule. A rule
        has two parts: conditions and actions. The conditions are the facts that
        are true with some degree-of-belief. The condition can specify a
        degree-of-belief that must be greater than a certain threshold. Actions
        are things to do to the KB when the rule is applied, generally resulting
        in new facts being added to the KB with degrees of membership or beleif.
        We previously showed an example in the beliefs that had rules.

        We might say that a football is somewhat round, a zebra is
        mostly black and white, and a person may be a male. Each of these
        beliefs can be represented as a conditions-actions pair or a fact.
        A conditions-actions pair

        - [{'cond':    [{'pred': 'is-football',
                         'args': ['?x'],
                         'deg': '?d',
                         'deg-pred': ['>', '?d', 0.5]}],
            'actions': [{'action': 'add',
                         'fact': {
                             'pred': 'is-round',
                             'args': ['?x'],
                             'deg': ['*', 0.7, '?d']}}]}

        - [{'cond':    [{'pred': 'is-person',
                         'args': ['?x'],
                         'deg': '?d',
                         'deg-pred': ['>', '?d', 0.9]}],
            'actions': [{'action': 'add',
                         'fact': {
                             'pred': 'is-male',
                             'args': ['?x'],
                             'deg': ['*', 0.5, '?d']}}]}

      Of course, we may have additional facts (beliefs) that can provide
      more information about the world. For example, we may have the fact
      that Sam is a male with a degree of membership of 1.0. How do we resolve
      the degree-of-truth or membershp for a fact? We simply take the maximum of
      the degree of membership of the fact that Sam is a male. This is equivalent
      to taking the `fuzzy-or` of the degrees of membership of each fact.

    - Set-theoretic predicates: Set-theoretic predicates are predicates that
      can specify `or`, `and`, and `not` predicates on conditions. By default,
      when we provide a list of conditions for a rule, we assume that we
      'and' them. However, we can also specify 'or' and 'not' predicates and
      even 'and` if we want to be explicit. For example, we can specify that
      if something is a mammal and does not have hair, then it is a
      shaven animal. We can also specify that if something is a mammal or
      has hair, then it is a hairy animal. We would represent these rules as
      follows:

        - [{'cond':    [{'or': [{'pred': 'is-mammal', 'args': ['?x']},
                                {'pred': 'has-hair', 'args': ['?x']}]}],
            'actions': [{'action': 'add',
                         'fact': {
                             'pred': 'is-hairy-animal',
                             'args': ['?x']}}]}

        - [{'cond':    [{'pred': 'is-mammal', 'args': ['?x']},
                        {'not': {'pred': 'has-hair', 'args': ['?x']}}]}],
            'actions': [{'action': 'add',
                         'fact': {
                             'pred': 'is-shaven-animal',
                             'args': ['?x']}}]}

    - Fuzzy inference: Fuzzy inference is the process of applying the rules to
        fuzzy facts to infer new facts. It is a type of inference that deals with
        uncertainty. In fuzzy inference, the facts can have degrees of membership
        in a set. For example, the fact "Sam is a zebra" can have a degree of
        membership in the set of zebras. This degree of membership can be used to
        infer new facts with degrees of membership. We would represent this
        fact as `[{pred: "is-zebra", args: ["sam"], degree: 0.8}]`. If `degree`
        is not specified, it is assumed to be 1, i.e., the fact is true.
        Likewise, if the degree is 0, the fact is false, although typically
        we would not represent false facts in the knowledge base.


        The algorithm is as follows:
        - For each rule, check if the facts satisfy the conditions.
        - If the conditions are satisfied, apply the actions.
        - Repeat until the KB does not change after applying the rules.

        Since we have a more complicated inference system, efficient algorithms
        like the Rete algorithm are not applicable. We use brute-force
        forward-chaining by iterating over the rules and checking if the facts
        satisfy the conditions. This is a simple implementation that is easy to
        extend, modify, and debug. It is, however, orders of magnitude slower
        than non-fuzzy production rule systems like the Rete algorithm. We prefer
        simple implementations for pedagogical purposes, as it is difficult
        enough to understand fuzzy inference without the added complexity of a
        sophisticated algorithm.

    Future plans:

    - Integrate with an large language model (LLM) that can "infer" new rules
      dynamically based on existing rules and facts. We do not necessarily need
      to define all of the rules upfront. We can start with a few rules and let
      the system generate new rules as needed, using the general intelligence of
      the LLM. This is a form of "meta-learning" where the system learns how to
      learn rules and can also generate new facts based on the existing facts,
      without an application of rules or human intervention.
    """

    def __init__(self):
        self.facts = list()
        self.rules = list()

    def add_rule(self, rule: Dict):
        """
        Add a rule to the rule engine.

        A rule is a dictionary with the following keys:
        - name: Rule name
        - description: Rule description (optional)
        - conds: List of conditions
        - actions: List of actions
        
        """
        self.rules.append(rule)

    def add_rules(self, rules: List) -> None:
        """
        Add multiple rules to the rule engine.

        :param rules: List of rules
        """
        self.rules.extend(rules)

    def add_fact(self, fact):
        self.facts.append(fact)

    def add_facts(self, facts):
        self.facts.extend(facts)

    def add_facts_from_dict(self, facts):
        for fact in facts:
            self.facts.append([fact['pred'], fact['args']])

    def act(self, actions) -> None:
        """
        Apply the actions to the facts.

        An action is a dictionary with the following keys:
        - action: 'add' or 'disable'
        - fact: Dictionary with the following keys:
            - pred: Predicate
            - args: List of arguments
        
        :param actions: List of actions
        """
        for action in actions:
            if action['action'] == 'add':
                fact = [action['fact']['pred'], action['fact']['args']]
                self.facts.append(fact)
            elif action['action'] == 'disable':
                pass

    def ask(self, question) -> Dict:
        """
        Ask a question to the inference engine.

        For example, to ask "Is Socrates mortal?", we are looking for a fact
        with a condition predicate "is-mortal" and the argument "Socrates".

        We iterate over the facts and look for a fact with the predicate
        "is-mortal" and the argument "Socrates". We apply the rules to the facts
        and check if we can infer the answer.

        ```json
        ans = inf.ask([["is-mortal", ["Socrates"]]])
        ```
 
        Note that we can also ask questions with variables. For example, to ask
        "Who are dwarvenn wizards that knows conjuration and is married?", we can use the following code:

        ```json
        ans = inf.ask(["uses-conjuration", ["?x"]],
                      ["is-dwarven", ["?x"]],  
                      ["is-wizard", ["?x"]],
                      ["or", ["is-married", ["?x", "?y"]],
                             ["is-married", ["?y", "?x"]]
                      ])
        ```

        The answer will be a list of facts that satisfy the condition. In this
        case, it will be a list of all the mortals.

        :param question: 
        """

        conds = dict()
        for cond, args in question:
            conds.append({"pred": cond, "args": args})

        self.run()
        # more code here


    def satisfies(self, conds) -> bool:
        """
        Check if the facts satisfy the conditions.

        A condition is a dictionary with the following keys:
        - pred: Predicate
        - args: List of arguments

        :param conds: List of conditions
        :return: True if the facts satisfy the conditions, False otherwise
        """
        for cond in conds:
            cond_pred, cond_args = cond['pred'], cond['args']
            for fact in self.facts:
                fact_pred, fact_args = fact[0], fact[1]
                if fact_pred == cond_pred and len(fact_args) == len(cond_args):
                    bindings = {}
                    all_match = True
                    for cond_arg, fact_arg in zip(cond_args, fact_args):
                        if cond_arg.startswith("?"):
                            if cond_arg in bindings and bindings[cond_arg] != fact_arg:
                                all_match = False
                                break
                            bindings[cond_arg] = fact_arg
                        elif cond_arg != fact_arg:
                            all_match = False
                            break
                    if all_match:
                        break
            else:
                return False
        return True

    def run(self):
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if self.satisfies(rule['cond']):
                    self.act(rule['actions'])
                    changed = True


    def apply_rule(self, rule, facts):
        for action in rule['actions']:
            if action['action'] == 'add':
                fact = [action['fact']['pred'], action['fact']['args']]
                facts.append(fact)
            elif action['action'] == 'disable':
                pass

