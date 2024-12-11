# Rules AST representation
rules = [
    {
        "name": "init",
        "desc": "Automatically triggered when we run the inference engine.",
        "conds": [
            {"pred": "true", "args": []}
        ],
        "actions": [
            {"action": "add", "fact": {"pred": "is-zebra", "args": ["sam"]}},
            {"action": "add", "fact": {"pred": "is-milk-giver", "args": ["animal"]}},
            {"action": "add", "fact": {"pred": "has-hooves", "args": ["animal"]}},
            {"action": "add", "fact": {"pred": "has-black-stripes", "args": ["animal"]}},
            {"action": "disable", "target": "self"}
        ]
    },
    {
        "name": "mammal-1",
        "desc": "A mammal is an animal with hair",
        "conds": [
            {"pred": "has-hair", "args": ["?h"]}
        ],
        "actions": [
            {"action": "add", "fact": {"pred": "is-animal", "args": ["?h"]}}
        ]
    },
    {
        "name": "mammal-2",
        "desc": "A mammal is a milk giver",
        "conds": [
            {"pred": "is-milk-giver", "args": ["?m2"]}
        ],
        "actions": [
            {"action": "add", "fact": {"pred": "is-mammal", "args": ["?m2"]}}
        ]
    },
]
