from ecs_simulator import *

Library.author("Igor Peretta")

Not = Gate('Not', 1, ['in'], ['out'])
Not.set_as_vcc(0, 'C')
Not.set_as_gnd(0, 'E')
Not.set_as_input(0, 'B', 'in')
Not.set_as_output(0, 'C', 'out')
Not.save()

Not.test_all()

And = Gate('And', 2, ['a', 'b'], ['out'])
And.set_as_vcc(0, 'C')
And.set_as_gnd(1, 'E')
And.connect(0, 'E', 1, 'C')
And.set_as_input(0, 'B', 'a')
And.set_as_input(1, 'B', 'b')
And.set_as_output(1, 'E', 'out')
And.save()

And.test_all()

Or = Gate('Or', 2, ['a', 'b'], ['out'])
Or.set_as_vcc(0, 'C')
Or.set_as_gnd(1, 'E')
Or.connect(0, 'C', 1, 'C')
Or.connect(0, 'E', 1, 'E')
Or.set_as_input(0, 'B', 'a')
Or.set_as_input(1, 'B', 'b')
Or.set_as_output(1, 'E', 'out')
Or.save()

Or.test_all()

Mux = Circuit('Mux', ['a', 'b', 'sel'], 'out')
Mux.add_components(Not, (And, 2), Or)
Mux.set_as_input(1, 'a', 'a')
Mux.set_as_input(2, 'b', 'b')
Mux.set_as_output(3, 'out', 'out')
Mux.connect(1, 'out', 3, 'a')
Mux.connect(2, 'out', 3, 'b')
Mux.set_as_input(1, 'b', 'sel')
Mux.set_as_input(0, 'in', 'sel')
Mux.connect(0, 'out', 2, 'a')
Mux.save()

Mux.test_all()
