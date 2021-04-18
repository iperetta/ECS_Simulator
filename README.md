# ECS_Simulator
Simulador para o curso de Elementos de Sistemas Computacionais (*Elements of Computing Systems*) da FEELT/UFU/Brasil, programado para Python 3.6+. Inspirado pelo curso http://nand2tetris.org.

## Exemplos de uso:

- Para importar o módulo:

        from ecs_simulator import *

- Para registrar a autoria dos seus componentes (única vez no início do seu script):

        Library.author("seu nome aqui")
        
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
    
    Resultado (`XXXX` é o identificador da instância do componente):

        Nand_XXXX : I/O 2⨉1 [#Q 2]
        ------------
         a, b | out
        ------------
         0, 0 | 1
         0, 1 | 1
         1, 0 | 1
         1, 1 | 0
        ------------
    
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

    Resultado (`XXXX` é o identificador da instância do componente):
    
        Xor_XXXX : I/O 2⨉1 [#Q 6]
        ------------
         a, b | out
        ------------
         0, 0 | 0
         0, 1 | 1
         1, 0 | 1
         1, 1 | 0
        ------------
         
- Para construir um circuito lógico a partir de outros circuitos com auxílio da função `lbs` criada para isso:

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

    Resultado (`XXXX` é o identificador da instância do componente):
    
        Mux16_XXXX : I/O 33⨉16 [#Q 112]
        --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         sel, a15, a14, a13, a12, a11, a10, a9, a8, a7, a6, a5, a4, a3, a2, a1, a0, b15, b14, b13, b12, b11, b10, b9, b8, b7, b6, b5, b4, b3, b2, b1, b0 | out15, out14, out13, out12, out11, out10, out9, out8, out7, out6, out5, out4, out3, out2, out1, out0
        --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
         0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
         
    A função `lbs` é definida por (veja no código para maiores detalhes):

        def lbs(prefix, length) ---
        prefix is any word you want to start a reversed enumerated sequence of labels:
            ex. lbs('in', 4) => ['in3', 'in2', 'in1', 'in0']
        prefix='@' and length <= 26 will return an alphabetical sequence of letters:
            ex. lbs('@', 4) => ['a', 'b', 'c', 'd']
        if you want to use '@' as a prefix, use '\@':
            ex. lbs('\@', 4) => ['@3', '@2', '@1', '@0']

- Uso de funções do Python pode auxiliar na definição de *labels* para entradas e saídas, além de facilitar a descrição de entradas e saídas com laços:

        from functools import reduce
        # ...
        ## assuming Mux4way.sim circuit is available in /lib:
        Mux4way16 = Circuit('Mux4way16', 
            reduce(lambda a, b: a+b, list(lbs(x, 16) for x in lbs('@', 4))) + lbs('sel', 2), 
            lbs('out', 16)
        )
        Mux4way16.add_components((Library.load('Mux4way'), 16))
        for i in range(16):
            for x in lbs('@', 4):
                Mux4way16.set_as_input(i, x, f'{x}{i}')
            Mux4way16.set_as_input(i, 'sel0', 'sel0')
            Mux4way16.set_as_input(i, 'sel1', 'sel1')
            Mux4way16.set_as_output(i, 'out', f'out{i}')
        Mux4way16.save()    
        Mux4way16.test_set(
            [
                [1]*16 + [0]*16 + [0]*16 + [0]*16 + [0, 0],
                [0]*16 + [1]*16 + [0]*16 + [0]*16 + [0, 1],
                [0]*16 + [0]*16 + [1]*16 + [0]*16 + [1, 0],
                [0]*16 + [0]*16 + [0]*16 + [1]*16 + [1, 1],
            ], 
            label_display_order=lbs('sel', 2) + \
                reduce(lambda a, b: a+b, list(lbs(x, 16) for x in lbs('@', 4))), 
            compact=True
        )

    Resultado (`XXXX` é o identificador da instância do componente) com parâmetro `compact=True` nos testes:
    
        Mux4way16_XXXX : I/O 66⨉16 [#Q 336]
        -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        s s a a a a a a a a a a a a a a a a b b b b b b b b b b b b b b b b c c c c c c c c c c c c c c c c d d d d d d d d d d d d d d d d | o o o o o o o o o o o o o o o o
        e e 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 | u u u u u u u u u u u u u u u u
        l l 5 4 3 2 1 0                     5 4 3 2 1 0                     5 4 3 2 1 0                     5 4 3 2 1 0                     | t t t t t t t t t t t t t t t t
        1 0                                                                                                                                 | 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0
                                                                                                                                            | 5 4 3 2 1 0                    
        -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 | 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
        0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 | 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
        1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 | 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
        1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 | 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
        -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Uso de testes aritméticos:

        ## assuming Alu.sim circuit is available in /lib:
        Alu = Library.load('Alu') 
        # definition: 
        #  Alu = Circuit('Alu', 
        #    lbs('x', 16) + lbs('y', 16) + ['zx', 'nx', 'zy', 'ny', 'f', 'no'], 
        #    lbs('out', 16) + ['zr', 'ng']
        #  )
        Alu.test_arithm(msg="x+y", 
            x=10, y=12, zx=0, nx=0, zy=0, ny=0, f=1, no=0, 
            label_display_order=(
                ['zx', 'nx', 'zy', 'ny', 'f', 'no'] + lbs('x', 16) + lbs('y', 16), 
                ['zr', 'ng'] + lbs('out', 16)
            ), 
            unsigned=['zx', 'nx', 'zy', 'ny', 'f', 'no', 'zr', 'ng'])
        Alu.test_arithm(msg="x-y", 
            x=10, y=12, zx=0, nx=1, zy=0, ny=0, f=1, no=1, 
            label_display_order=(
                ['zx', 'nx', 'zy', 'ny', 'f', 'no'] + lbs('x', 16) + lbs('y', 16), 
                ['zr', 'ng'] + lbs('out', 16)
            ), 
            unsigned=['zx', 'nx', 'zy', 'ny', 'f', 'no', 'zr', 'ng'])
        Alu.test_arithm(msg="x&y", 
            x=10, y=12, zx=0, nx=0, zy=0, ny=0, f=0, no=0, 
            label_display_order=(
                ['zx', 'nx', 'zy', 'ny', 'f', 'no'] + lbs('x', 16) + lbs('y', 16), 
                ['zr', 'ng']+lbs('out', 16)
            ), 
            unsigned=['zx', 'nx', 'zy', 'ny', 'f', 'no', 'zr', 'ng'])

    Resultado (`XXXX` é o identificador da instância do componente); note que parâmetro `compact=True` é o padrão para os testes:

        Alu_XXXX : I/O 38⨉18 [#Q 1046]
        -------------------------------------------------------------------------------------------------------------------
        z n z n f n x x x x x x x x x x x x x x x x y y y y y y y y y y y y y y y y | z n o o o o o o o o o o o o o o o o
        x x y y   o 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 | r g u u u u u u u u u u u u u u u u
                    5 4 3 2 1 0                     5 4 3 2 1 0                     |     t t t t t t t t t t t t t t t t
                                                                                    |     1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0
                                                                                    |     5 4 3 2 1 0                    
        -------------------------------------------------------------------------------------------------------------------
        0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 | 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 0
        ------------------------------------------------------------------------------------------------------------------
        received inputs (decimal): zx=0, nx=0, zy=0, ny=0, f=1, no=0, x=10, y=12
        operation [X+Y] applied to:  zx=0, nx=0, zy=0, ny=0, f=1, no=0, x=10, y=12 | result:  zr=0, ng=0, out=22
        ------------------------------------------------------------------------------------------------------------------
        
        Alu_XXXX : I/O 38⨉18 [#Q 1046]
        -------------------------------------------------------------------------------------------------------------------
        z n z n f n x x x x x x x x x x x x x x x x y y y y y y y y y y y y y y y y | z n o o o o o o o o o o o o o o o o
        x x y y   o 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 | r g u u u u u u u u u u u u u u u u
                    5 4 3 2 1 0                     5 4 3 2 1 0                     |     t t t t t t t t t t t t t t t t
                                                                                    |     1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0
                                                                                    |     5 4 3 2 1 0                    
        -------------------------------------------------------------------------------------------------------------------
        0 1 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 | 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0
        ------------------------------------------------------------------------------------------------------------------
        received inputs (decimal): zx=0, nx=1, zy=0, ny=0, f=1, no=1, x=10, y=12
        operation [X-Y] applied to:  zx=0, nx=1, zy=0, ny=0, f=1, no=1, x=10, y=12 | result:  zr=0, ng=1, out=-2
        ------------------------------------------------------------------------------------------------------------------

        Alu_XXXX : I/O 38⨉18 [#Q 1046]
        -------------------------------------------------------------------------------------------------------------------
        z n z n f n x x x x x x x x x x x x x x x x y y y y y y y y y y y y y y y y | z n o o o o o o o o o o o o o o o o
        x x y y   o 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0 | r g u u u u u u u u u u u u u u u u
                    5 4 3 2 1 0                     5 4 3 2 1 0                     |     t t t t t t t t t t t t t t t t
                                                                                    |     1 1 1 1 1 1 9 8 7 6 5 4 3 2 1 0
                                                                                    |     5 4 3 2 1 0                    
        -------------------------------------------------------------------------------------------------------------------
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 | 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0
        ------------------------------------------------------------------------------------------------------------------
        received inputs (decimal): zx=0, nx=0, zy=0, ny=0, f=0, no=0, x=10, y=12
        operation [X&Y] applied to:  zx=0, nx=0, zy=0, ny=0, f=0, no=0, x=10, y=12 | result:  zr=0, ng=0, out=8
        ------------------------------------------------------------------------------------------------------------------
    
    Note que a Alu implementada possui 1046 transistores.