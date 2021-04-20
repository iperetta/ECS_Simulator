from ecs_simulator import *

Library.author("Igor Peretta")

HalfAdder = Circuit('HalfAdder', ['a', 'b'], ['sum', 'carry'])
HalfAdder.add_components(
    Library.load('Xor'),
    Library.load('And')
)
HalfAdder.set_as_input(0, 'a', 'a')
HalfAdder.set_as_input(0, 'b', 'b')
HalfAdder.set_as_input(1, 'a', 'a')
HalfAdder.set_as_input(1, 'b', 'b')
HalfAdder.set_as_output(0, 'out', 'sum')
HalfAdder.set_as_output(1, 'out', 'carry')
HalfAdder.save()
HalfAdder.test_all(label_display_order=([], ['carry', 'sum']), compact=True)

# FullAdder = Circuit('FullAdder', ['a', 'b', 'c'], ['sum', 'carry'])
# FullAdder.add_components(
#     (Library.load('Xor'), 2),
#     (Library.load('And'), 2),
#     Library.load('Or')
# )
# FullAdder.set_as_input(0, 'a', 'a')
# FullAdder.set_as_input(0, 'b', 'b')
# FullAdder.set_as_input(2, 'a', 'a')
# FullAdder.set_as_input(2, 'b', 'b')
# FullAdder.set_as_input(1, 'b', 'c')
# FullAdder.set_as_input(3, 'b', 'c')
# FullAdder.set_as_output(1, 'out', 'sum')
# FullAdder.set_as_output(4, 'out', 'carry')
# FullAdder.connect(0, 'out', 1, 'a')
# FullAdder.connect(0, 'out', 3, 'a')
# FullAdder.connect(2, 'out', 4, 'a')
# FullAdder.connect(3, 'out', 4, 'b')
# FullAdder.test_all()

FullAdder = Circuit('FullAdder', ['a', 'b', 'c'], ['sum', 'carry'])
FullAdder.add_components(
    (HalfAdder, 2),
    Library.load('Or')
)
FullAdder.set_as_input(0, 'a', 'a')
FullAdder.set_as_input(0, 'b', 'b')
FullAdder.set_as_input(1, 'b', 'c')
FullAdder.connect(0, 'sum', 1, 'a')
FullAdder.set_as_output(1, 'sum', 'sum')
FullAdder.connect(0, 'carry', 2, 'a')
FullAdder.connect(1, 'carry', 2, 'b')
FullAdder.set_as_output(2, 'out', 'carry')
FullAdder.save()
FullAdder.test_all(label_display_order=([], ['carry', 'sum']))

Add16 = Circuit('Add16', lbs('a', 16) + lbs('b', 16), lbs('out', 16))
Add16.add_components(
    HalfAdder,
    (FullAdder, 15)
)
for i in range(16):
    Add16.set_as_input(i, 'a', f'a{i}')
    Add16.set_as_input(i, 'b', f'b{i}')
    Add16.set_as_output(i, 'sum', f'out{i}')
for i in range(1, 16):
    Add16.connect(i - 1, 'carry', i, 'c')
Add16.save()
Add16.test_arithm(a=7, b=5)
Add16.test_arithm(a=-128, b=85)
Add16.test_arithm(a=2**16-1, b=85)
Add16.test_arithm(a=100000, b=85)

Inc16 = Circuit('Inc16', lbs('inp', 16), lbs('out', 16))
Inc16.add_components(Add16)
for i in range(16):
    Inc16.set_as_input(0, f'a{i}', f'inp{i}')
    Inc16.set_as_output(0, f'out{i}', f'out{i}')
Inc16.set_high_input(0, 'b0')
for i in range(1, 16):
    Inc16.set_low_input(0, f'b{i}')
Inc16.save()
Inc16.test_arithm(inp=128)
Inc16.test_arithm(inp=-1)
