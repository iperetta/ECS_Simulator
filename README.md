# ECS_Simulator
Simulador para o curso de Elementos de Sistemas Computacionais (*Elements of Computating Systems*) da FEELT/UFU/Brasil, programado para Python 3.6+. Inspirado pelo curso http://nand2tetris.org.

## Exemplos de uso:

- Para importar o módulo:

        from ecs_simulator import *

- Para construir uma porta lógica a partir de transistores:

        Nand = Gate('Nand', 2, ['a', 'b'], 'out') # 2 transistors
        Nand.set_as_vcc(0, 'C')
        Nand.set_as_gnd(1, 'E')
        Nand.set_as_input(0, 'B', 'a')
        Nand.set_as_input(1, 'B', 'b')
        Nand.set_as_output(1, 'C', 'out')
        Nand.connect(0, 'E', 1, 'C')
        Nand.test_all()
        Nand.save() # save it to library
    
        Nand.test_all()
    
    Resultado (`XXXX` é o identificador do componente):

        Nand_XXXX : I/O 2⨉1 [#Q 2]
        ------------
         a, b | out
        ------------
         0, 0 | 1
         0, 1 | 1
         1, 0 | 1
         1, 1 | 0
    
- Para construir um circuito lógico a partir de portas lógicas:

        ## assuming both Or.sim and And.sim gates are available in /lib:
        Xor = Circuit('Xor', ['a', 'b'], ['out'])
        Xor.add_components(Nand, Library.load('Or'), Library.load('And'))
        Xor.set_as_input(0, 'a', 'a')
        Xor.set_as_input(0, 'b', 'b')
        Xor.set_as_output(2, 'out', 'out')
        Xor.connect(0, 'a', 1, 'a')
        Xor.connect(0, 'b', 1, 'b')
        Xor.connect(0, 'out', 2, 'a')
        Xor.connect(1, 'out', 2, 'b')
        Xor.save() # save it to library

        Xor.test_all()

    Resultado (`XXXX` é o identificador do componente):
    
        Xor_XXXX : I/O 2⨉1 [#Q 6]
        ------------
         a, b | out
        ------------
         0, 0 | 0
         0, 1 | 1
         1, 0 | 1
         1, 1 | 0
         
- Para construir um circuito lógico a partir de outros circuitos:

        ## assuming Mux.sim circuit is available in /lib:
        Mux16 = Circuit('Mux16', lbs('a', 16) + lbs('b', 16) + ['sel'], lbs('out', 16))
        Mux16.add_components((Library.Load('Mux'), 16))
        for i in range(16):
            Mux16.set_as_input(i, 'a', f'a{i}')
            Mux16.set_as_input(i, 'b', f'b{i}')
            Mux16.set_as_input(i, 'sel', f'sel')
            Mux16.set_as_output(i, 'out', f'out{i}')
        Mux16.save() # save it to library

        Mux16.test_set([
            [0]*16 + [1]*16 + [0], [0]*16 + [1]*16 + [1], 
            [1]*16 + [0]*16 + [0], [1]*16 + [0]*16 + [1]
        ], label_display_order=['sel'] + lbs('a', 16) + lbs('b', 16))

    Resultado (`XXXX` é o identificador do componente):
    
        Mux16_XXXX : I/O 33⨉16 [#Q 112]
        --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         sel, a15, a14, a13, a12, a11, a10, a9, a8, a7, a6, a5, a4, a3, a2, a1, a0, b15, b14, b13, b12, b11, b10, b9, b8, b7, b6, b5, b4, b3, b2, b1, b0 | out15, out14, out13, out12, out11, out10, out9, out8, out7, out6, out5, out4, out3, out2, out1, out0
        --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
         0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
