;
;  Animal Identification
;

(defrule init
	(true null)
=>
    (add (is-zebra sam))
	(add (is-milk-giver animal))
	(add (has-hooves animal))
	(add (has-black-stripes animal))
	(disable (self))
)

(defrule mammal-1
	(has-hair ?)
=>
	(add(is-animal ?))
)

(defrule mammal-2
	(is-milk-giver ?)
=>
	(add(is-mammal ?))
)

(defrule bird-1
	(has-feathers ?)
=>
	(add(is-bird ?))
)

(defrule bird-2
	(is-flier ?)
	(is-egg-layer ?)
=>
	(add(is-bird ?))
)

(defrule carnivore-1
	(is-meat-eater ?)
=>
	(add(is-carnivore ?))
)

(defrule carnivore-2
	(has-pointed-teeth ?)
	(has-claws ?)
	(has-forward-eyes ?)
=>
	(add(is-carnivore ?))
)

(defrule ungulate-1
	(is-mammal ?)
	(has-hooves ?)
=>
	(add(is-ungulate ?))
)

(defrule ungulate-2
	(is-mammal ?)
	(is-cud-chewer ?)
=>
	(add(is-ungulate ?))
)

(defrule even-toed
	(is-mammal ?)
	(is-cud-chewer ?)
=>
	(add(is-even-toed ?))
)

(defrule cheetah
	(is-mammal ?)
	(is-carnivore ?)
	(is-tanwny-colored ?)
	(has-dark-spots ?)
=>
	(add(is-cheetah ?))
)

(defrule tiger
	(is-mammal ?)
	(is-carnivore ?)
	(is-tawny-colored ?)
	(has-black-strips ?)
=>
	(add(is-tiger ?))
)

(defrule giraffe
	(is-ungulate ?)
	(has-long-neck ?)
	(has-long-legs ?)
	(has-dark-spots ?)
=>
	(add(is-giraffe ?))
)

(defrule zebra
	(is-ungulate ?)
	(has-black-stripes ?)
=>
	(add(is-zebra ?))
)
