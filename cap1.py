from ecs_simulator import *

Library.author("Igor Peretta")

Not = Gate('Not', 1, ['in'], ['out'])
Not.set_as_vcc(0, 'C')
Not.set_as_gnd(0, 'E')
Not.set_as_input(0, 'B', 'in')
Not.set_as_output(0, 'C', 'out')
Not.save()

Not_b = Library.load('Not')
Not_b.test_all()

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
Mux.set_as_input(1, 'b', 'a')
Mux.set_as_input(2, 'b', 'b')
Mux.set_as_output(3, 'out', 'out')
Mux.connect(1, 'out', 3, 'a')
Mux.connect(2, 'out', 3, 'b')
Mux.set_as_input(0, 'in', 'sel')
Mux.set_as_input(2, 'a', 'sel')
Mux.connect(0, 'out', 1, 'a')
Mux.save()

Mux.test_all(label_display_order=['sel', 'a', 'b'])


Mux16 = Circuit('Mux16', lbs('a', 16)+lbs('b', 16)+['sel'], lbs('out', 16))
Mux16.add_components((Mux, 16))
for i in range(16):
    Mux16.set_as_input(i, 'a', f'a{i}')
    Mux16.set_as_input(i, 'b', f'b{i}')
    Mux16.set_as_input(i, 'sel', 'sel')
    Mux16.set_as_output(i, 'out', f'out{i}')
Mux16.save()

Mux16.test_set([
    [1]*16 + [0]*16 + [0],
    [0]*16 + [1]*16 + [1],
], label_display_order=['sel']+lbs('a', 16)+lbs('b', 16))

Or8way = Gate('Or8way', 8, lbs('in', 8), 'out')
Or8way.set_as_vcc(0, 'C')
Or8way.set_as_gnd(0, 'E')
for i in range(1, 8):
    Or8way.connect(0, 'C', i, 'C')
    Or8way.connect(0, 'E', i, 'E')
for i in range(8):
    Or8way.set_as_input(i, 'B', f'in{i}')
Or8way.set_as_output(0, 'E', 'out')
Or8way.save()

Or8way.test_all()


Mux4way = Circuit('Mux4way', lbs('@', 4)+['sel1', 'sel0'], 'out')
Mux4way.add_components((Mux, 3))
Mux4way.set_as_input(2, 'sel', 'sel1')
Mux4way.set_as_input(0, 'sel', 'sel0')
Mux4way.set_as_input(1, 'sel', 'sel0')
Mux4way.set_as_input(0, 'a', 'a')
Mux4way.set_as_input(0, 'b', 'b')
Mux4way.set_as_input(1, 'a', 'c')
Mux4way.set_as_input(1, 'b', 'd')
Mux4way.set_as_output(2, 'out', 'out')
Mux4way.connect(0, 'out', 2, 'a')
Mux4way.connect(1, 'out', 2, 'b')
Mux4way.save()

Mux4way.test_all(label_display_order=['sel1', 'sel0']+lbs('@', 4))

