# ECS_Simulator
Simulador para o curso de Elementos de Sistemas Computacionais (*Elements of Computating Systems*) da FEELT/UFU/Brasil, programado para Python 3.6+.

## Exemplos de uso:

    from ecs_simulator import *
    
    And = Gate('And', 2, ['a', 'b'], ['out'])
    And.set_as_vcc(0, 'C')
    And.set_as_gnd(1, 'E')
    And.set_as_input(0, 'B', 'a')
    And.set_as_input(1, 'B', 'b')
    And.set_as_output(1, 'E', 'out')
    And.connect(0, 'E', 1, 'C')
    And.save()
    
    And.test_all()
    
    ## assuming both Nand and Or gates are available:
    
    Xor = Circuit('Xor', ['a', 'b'], ['out'])
    Xor.add_components(Library.load('Nand'), Library.load('Or'), And)
    Xor.set_as_input(0, 'a', 'a')
    Xor.set_as_input(0, 'b', 'b')
    Xor.set_as_output(2, 'out', 'out')
    Xor.connect(0, 'a', 1, 'a')
    Xor.connect(0, 'b', 1, 'b')
    Xor.connect(0, 'out', 2, 'a')
    Xor.connect(1, 'out', 2, 'b')
    Xor.save()
    
    Xor.test_all()
    
    ## assuming Mux circuit is available:
    
    Mux16 = Circuit('Mux16', lbs('a', 16) + lbs('b', 16) + ['sel'], lbs('out', 16))
    Mux16.add_components((Mux, 16))
    for i in range(16):
        Mux16.set_as_input(i, 'a', f'a{i}')
        Mux16.set_as_input(i, 'b', f'b{i}')
        Mux16.set_as_input(i, 'sel', f'sel')
        Mux16.set_as_output(i, 'out', f'out{i}')
    Mux16.save()
    
    Mux16.test_set([
        [0]*16 + [1]*16 + [0], [0]*16 + [1]*16 + [1], 
        [1]*16 + [0]*16 + [0], [1]*16 + [0]*16 + [1]
    ], label_order=['sel'] + lbs('a', 16) + lbs('b', 16))
