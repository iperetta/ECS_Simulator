import uuid
import pickle
import os
from pathlib import Path


def lbs(prefix, length):
    """
    prefix is any word you want to start a reversed enumerated sequence of labels:
        ex. lbs('in', 4) => ['in3', 'in2', 'in1', 'in0']
    prefix='@' and length <= 26 will return an alphabetical sequence of letters:
        ex. lbs('@', 4) => ['a', 'b', 'c', 'd']
    if you want to use '@' as a prefix, use '\@':
        ex. lbs('\@', 4) => ['@3', '@2', '@1', '@0']
    """
    if prefix == '@' and length < 27:
        return list(f"{chr(97 + i)}" for i in range(length))
    else:
        if prefix == '@': prefix = 'in'
        elif prefix == '\@': prefix = '@'
        return list(f"{prefix}{i}" for i in reversed(range(length)))


class Library:
    dirpath = Path('lib')
    cc_by = None
    @classmethod
    def author(cls, identifier):
        cls.cc_by = identifier
    @classmethod
    def change_ospath(cls, identifier):
        cls.dirpath = Path(identifier)
    @staticmethod
    def load(filename):
        if not filename.endswith('.sim'):
            filename += '.sim'
        with open(Library.dirpath / filename, 'rb') as f:
            aux = pickle.load(f)
        return aux.copy()
    def __init__(self, name):
        self.name = name
        self.id = uuid.uuid4()
    def error(self, msg):
        raise Exception(f"{self}: {msg}")
    def save(self, filename=None):
        if filename is None:
            filename = self.name + '.sim'
        with open(Library.dirpath / filename, 'wb') as f:
            pickle.dump(self, f)
    def __repr__(self):
        return f"{self.name}_{str(self.id)[-4:].upper()}"


if not os.path.isdir(Library.dirpath):
    os.mkdir(Library.dirpath)


class Wire(Library):
    def __init__(self, init=0, changeable=True, name='Wire'):
        super().__init__(name)
        self.next = False if init == 0 else True
        self.changeable = changeable
    def __lt__(self, other):
        return self.id < other.id
    def set_high(self):
        if self.changeable: self.next = True
    def set_low(self):
        if self.changeable: self.next = False
    def set_as(self, other):
        if self.changeable: self.next = other.next
    def invert(self):
        if self.changeable and not self.next is None: self.next = not self.next
    def disconnect(self):
        if self.changeable: self.next = None
    def is_disconnect(self):
        return self.next is None
    def copy(self):
        return Wire(init=self.next, changeable=self.changeable, name=self.name)
    def __repr__(self):
        return super().__repr__() + f"[{'H' if self.next else ('?' if self.next is None else 'L')}]"


if os.path.isfile(Library.dirpath / 'VCC.sim'): 
    VCC = Library.load('VCC.sim')
else:
    VCC = Wire(1, changeable=False, name='VCC')
    VCC.save()

if os.path.isfile(Library.dirpath / 'GND.sim'): 
    GND = Library.load('GND.sim')
else:
    GND = Wire(0, changeable=False, name='GND')
    GND.save()


class Bus(Library):
    def __init__(self, nrbits):
        super().__init__('Bus')
        self.nrbits = nrbits
        self.binvec = list(Wire() for _ in range(self.nrbits))
        self.labels = list(reversed(range(self.nrbits))) #@verify
    def __getitem__(self, index):
        return self.binvec[index] if type(index) == int else self.binvec[self.labels.index(index)]
    def copy(self):
        aux = Bus(self.nrbits)
        aux.set_labels(*self.labels)
        return aux
    def set_label(self, index, label):
        self.labels[index] = label
    def set_labels(self, *args):
        if len(args) == 1 and type(args[0]) in [list, tuple]:
            args = args[0]
        if len(args) == len(self.labels):
            for i, l in enumerate(args):
                self.set_label(i, l)
        else:
            self.error(f"wrong number of labels, expecting {self.nrbits}, not {args}.")
    def _convert_to_binary(self, decimal, nrbits):
        binvec = list(True if b == '1' else False for b in bin(decimal)[2:])
        lb = len(binvec)
        if lb < nrbits:
            binvec = [False]*(nrbits - lb) + binvec
        else:
            binvec = binvec[lb - nrbits:]
        return binvec
    def _convert_to_decimal(self):
        decimal = 0
        for n, b in enumerate(self.binvec): #@verify
            if b.next:
                decimal += 2**n
        return decimal
    def set_as(self, data):
        if type(data) == int:
            aux = self._convert_to_binary(data, self.nrbits)
            for i in range(self.nrbits):
                self.binvec[i].next = aux[i]
        elif type(data) == list and len(data) == self.nrbits:
            if type(data[0]) in [bool, int]:
                for i in range(self.nrbits):
                    self.binvec[i].next = True if data[i] == 1 else False
            elif type(data[0]) == Wire:
                for i in range(self.nrbits):
                    self.binvec[i].next = data[i].next
        elif type(data) == Bus and data.nrbits == self.nrbits:
            for i in range(self.nrbits):
                self.binvec[i].next = data.binvec[i].next
        else:
            self.error("cannot set bus, please review.")
    def get_wires(self):
        return self.binvec
    def str(self, sep='', order=None):
        if order is None: order = self.labels
        return sep.join(list('1' if b.next else '0' for b in \
            list(self.binvec[self.labels.index(l)] for l in order)))


class Transistor(Library):
    def __init__(self):
        super().__init__('Q')
        self.ports = { 'B': Wire(), 'C': Wire(), 'E': Wire() }
        self.bridge_CE = False
    def __getitem__(self, index):
        return self.ports[index]
    def copy(self):
        return Transistor()
    def logic(self):
        if self.ports['B'].next:
            self.bridge_CE = True
        else:
            self.bridge_CE = False
    def get_wires(self):
        return list(self.ports[l] for l in ['B', 'C', 'E'])


class Gate(Library):
    def __init__(self, name, nrtransistors, input_labels, output_labels):
        super().__init__(name)
        if type(input_labels) == str:
            input_labels = [input_labels]
        if type(output_labels) == str:
            output_labels = [output_labels]
        self.inputs = Bus(len(input_labels))
        self.inputs.set_labels(input_labels)
        self.outputs = Bus(len(output_labels))
        self.outputs.set_labels(output_labels)
        self.components = list(Transistor() for _ in range(nrtransistors))
        self.connections = dict((w, set()) for w in self.get_wires())
        self.inverted_outputs = dict((self.outputs[l], False) for l in self.outputs.labels) \
            if nrtransistors > 0 else None
        self.visited = None
    def __getitem__(self, index):
        if type(index) == int or index in self.inputs.labels:
           return self.inputs[index] 
        if type(index) == int or index in self.outputs.labels:
           return self.outputs[index]
    def get_wires(self):
        wires = [VCC, GND]
        wires += list(self.inputs[l] for l in self.inputs.labels)
        wires += list(self.outputs[l] for l in self.outputs.labels)
        for q in self.components:
            wires += q.get_wires()
        return wires
    def nrtransistors(self):
        return len(self.components)
    def copy(self):
        acopy = Gate(self.name, self.nrtransistors(), self.inputs.labels, self.outputs.labels)
        wires_dict = dict((ws, wc) for ws, wc in zip(self.get_wires(), acopy.get_wires()))
        for k, v in self.connections.items():
            acopy.connections[wires_dict[k]] = set(wires_dict[w] for w in v)
        for k, v in self.inverted_outputs.items():
            acopy.inverted_outputs[wires_dict[k]] = v
        return acopy
    def connect_nodes_unidirecional(self, wireFrom, wireTo):
        self.connections[wireFrom].add(wireTo)
    def connect_nodes(self, wireA, wireB):
        self.connections[wireA].add(wireB)
        self.connections[wireB].add(wireA)
    def disconnect_nodes(self, wireA, wireB):
        if wireB in self.connections[wireA]: self.connections[wireA].remove(wireB)
        if wireA in self.connections[wireB]: self.connections[wireB].remove(wireA)
    def connect(self, idxQA, portQA, idxQB, portQB):
        qpA = self.components[idxQA].ports[portQA]
        qpB = self.components[idxQB].ports[portQB]
        self.connect_nodes(qpA, qpB)
    def disconnect(self, idxQA, portQA, idxQB, portQB):
        qpA = self.components[idxQA].ports[portQA]
        qpB = self.components[idxQB].ports[portQB]
        self.disconnect_nodes(qpA, qpB)
    def set_as_input(self, idxQ, portQ, label):
        self.connect_nodes(self.components[idxQ].ports[portQ], self.inputs[label])
    def set_as_output(self, idxQ, portQ, label):
        self.connect_nodes(self.components[idxQ].ports[portQ], self.outputs[label])
        self.inverted_outputs[self.outputs[label]] = portQ == 'C'
    def set_as_vcc(self, idxQ, portQ):
        self.connect_nodes(self.components[idxQ].ports[portQ], VCC)
    def set_as_gnd(self, idxQ, portQ):
        self.connect_nodes(self.components[idxQ].ports[portQ], GND)
    def reset(self):
        for w in self.get_wires():
            w.disconnect()
    def is_input(self, label):
        return label in self.inputs.labels
    def is_output(self, label):
        return label in self.outputs.labels
    def _support_to_navigation(self):
        if self.visited is None:
            self.visited = dict((w, False) for w in self.get_wires())
        else:
            for k in self.visited.keys():
                self.visited[k] = False
    def _is_short_circuit(self, origin):
        if origin == GND:
            return True
        self.visited[origin] = True
        for w in self.connections[origin]:
            if not self.visited[w]:
                aux = self._is_short_circuit(w)
                if aux: return True
        return False
    def is_short_circuit(self):
        self._support_to_navigation()
        return self._is_short_circuit(VCC)
    def _propagate(self, origin):
        self.visited[origin] = True
        for w in self.connections[origin]:
            if not self.visited[w]:
                w.set_as(origin)
                self._propagate(w)
    def propagate(self, origin):
        self._support_to_navigation()
        self._propagate(origin)
    def set_input_values(self, values):
        if type(values) == list and len(values) == self.inputs.nrbits:
            d = dict()
            for i, l in enumerate(self.inputs.labels):
                d[l] = values[i]
            self.set_input_values(d)
        elif type(values) == dict:
            self.reset()
            for k, v in values.items():
                if v == 0: self.inputs[k].set_low()
                else: self.inputs[k].set_high()
        else:
            self.error(f"wrong number of values, expecting {self.inputs.nrbits}, not {len(values)}.")
    def logic(self):
        for q in self.components:
            q.logic()
            if q.bridge_CE: self.connect_nodes(q['C'], q['E'])
            else: self.disconnect_nodes(q['C'], q['E'])
    def run(self):
        for lbl in self.inputs.labels:
            self.propagate(self.inputs[lbl])
        self.logic()
        for l in self.outputs.labels:
            if self.is_short_circuit():
                self.outputs[l].next = not self.inverted_outputs[self.outputs[l]]
            else:
                self.outputs[l].next = self.inverted_outputs[self.outputs[l]]
    def header(self):
        return f"{self} : I/O {self.inputs.nrbits}⨉{self.outputs.nrbits} [#Q {self.nrtransistors()}]"
    def info(self):
        from pprint import pprint
        print(self, ': vcc', VCC, '; gnd', GND)
        for l in self.inputs.labels:
            print(l, self.inputs[l], end='; ')
        print('')
        for l in self.outputs.labels:
            print(l, self.outputs[l], end='; ')
        print('')
        for c in self.components:
            if type(c) == Transistor:
                print(c, c.ports)
            else:
                print(c, list((l, c.inputs[l]) for l in c.inputs.labels), list((l, c.outputs[l]) for l in c.outputs.labels))
        pprint(self.connections)
    def _test_header(self, input_labels):
        print('\n' + self.header())
        labels = ' ' + ', '.join(input_labels) + ' | ' + ', '.join(self.outputs.labels)
        print('-' + '-'*len(labels))
        print(labels)
        print('-' + '-'*len(labels))
    def test_all(self, label_order=None):
        input_labels = self.inputs.labels if label_order is None else label_order
        self._test_header(input_labels)
        dimension = len(input_labels)
        min_count, max_count = 0, 1
        counter = [min_count]*dimension
        while True:
            inputs = dict((k, v) for k, v in zip(input_labels, reversed(counter)))
            self.set_input_values(inputs)
            self.run()
            print(' ' + self.inputs.str(', ', order=input_labels) + ' | ' + self.outputs.str(', '))
            counter[0] += 1
            for i in range(len(counter)-1):
                if counter[i] > max_count:
                    counter[i] = min_count
                    counter[i+1] += 1
            if counter[-1] > max_count:
                break
        print('')


class Circuit(Gate):
    def __init__(self, name, input_labels, output_labels):
        super().__init__(name, 0, input_labels, output_labels)
        self.circuitry = dict()
        self.new_circuitry_entry(self)
    def new_circuitry_entry(self, key):
        self.circuitry[key] = { 'level': -1, 'same': [], 'children': [] }
    def get_wires(self):
        wires = list(self.inputs[l] for l in self.inputs.labels)
        wires += list(self.outputs[l] for l in self.outputs.labels)
        for q in self.components:
            wires += q.get_wires()
            wires.remove(VCC)
            wires.remove(GND)
        wires += [VCC, GND]
        return wires
    def copy(self):
        acopy = Circuit(self.name, self.inputs.labels, self.outputs.labels)
        for cp in self.components:
            acopy.add_component(cp)
        wires_dict = dict((ws, wc) for ws, wc in zip(self.get_wires(), acopy.get_wires()))
        for k, v in self.connections.items():
            acopy.connections[wires_dict[k]] = set(wires_dict[w] for w in v)
        comp_dict = dict((cs, cc) for cs, cc in zip(self.components, acopy.components))
        comp_dict.update({self: acopy})
        for k, v in self.circuitry.items():
            acopy.new_circuitry_entry(comp_dict[k])
            acopy.circuitry[comp_dict[k]]['level'] = v['level']
            acopy.circuitry[comp_dict[k]]['same'] = list(comp_dict[c] for c in v['same'])
            acopy.circuitry[comp_dict[k]]['children'] = list(comp_dict[c] for c in v['children'])
        return acopy
    def nrtransistors(self):
        return sum(cp.nrtransistors() for cp in self.components)
    def add_component(self, component):
        cp = component.copy()
        self.components.append(cp)
        for lbl in cp.inputs.labels:
            self.connections[cp[lbl]] = set()
        for lbl in cp.outputs.labels:
            self.connections[cp[lbl]] = set()
        self.new_circuitry_entry(cp)
    def add_components(self, *argv):
        for arg in argv:
            qty = 1
            if type(arg) == tuple:
                arg, qty = arg
            for _ in range(qty):
                self.add_component(arg)
    def connect_component_to(self, component_from, component_to, type_connection):
        """
        type_connection in {'same', 'children'}
        """
        if not component_from in self.circuitry:
            self.error(f"{component_from} is not registered.")
        if not component_to in self.circuitry[component_from][type_connection]:
            self.circuitry[component_from][type_connection].append(component_to)
    def connect(self, cidx_a, port_a, cidx_b, port_b):
        wire_a = self.components[cidx_a][port_a]
        wire_b = self.components[cidx_b][port_b]
        self.connect_nodes(wire_a, wire_b)
        if self.components[cidx_a].is_output(port_a) and self.components[cidx_b].is_input(port_b):
            self.connect_component_to(self.components[cidx_a], self.components[cidx_b], 'children')
        elif self.components[cidx_a].is_input(port_a) and self.components[cidx_b].is_output(port_b):
            self.connect_component_to(self.components[cidx_b], self.components[cidx_a], 'children')
        elif self.components[cidx_a].is_input(port_a) and self.components[cidx_b].is_input(port_b):
            self.connect_component_to(self.components[cidx_a], self.components[cidx_b], 'same')
        else: # both outputs
            self.error(f"connection {self.components[cidx_a][port_a]} to {self.components[cidx_b][port_b]} not allowed (both outputs).")
    def reset_circuitry_levels(self):
        self.circuitry[self]['level'] = -1
    def is_circuitry_uninitialized(self):
        return any(c['level'] < 0 for c in self.circuitry.values())
    def prepare_circuitry_levels(self, key=None, level=0):
        if key is None:
            key = self
        self.circuitry[key]['level'] = level
        for c in self.circuitry[key]['same']:
            if c != self:
                if self.circuitry[c]['level'] < level:
                    self.circuitry[c]['level'] = level
        for c in self.circuitry[key]['children']:
            if c != self:
                self.prepare_circuitry_levels(key=c, level=level+1)
    def set_components_in_order_to_run(self):
        for k, v in self.circuitry.items():
            for c in v['children']:
                if k in self.circuitry[c]['children']:
                    self.circuitry[c]['same'].append(k)
                    self.circuitry[c]['children'].remove(k)
                    self.circuitry[k]['same'].append(c)
                    self.circuitry[k]['children'].remove(c)
        if self.is_circuitry_uninitialized():
            self.prepare_circuitry_levels()
        raw = list((k, v['level']) for k, v in self.circuitry.items())
        sort_raw = sorted(raw, key=lambda x:x[1])
        ans = list(c[0] for c in sort_raw)
        ans.remove(self)
        return ans
    def set_as_input(self, cidx, port, label):
        wire = self.components[cidx][port]
        self.connect_nodes_unidirecional(self.inputs[label], wire)
        self.connect_component_to(self, self.components[cidx], 'children')
    def set_as_output(self, cidx, port, label):
        wire = self.components[cidx][port]
        self.connect_nodes_unidirecional(wire, self.outputs[label])
        self.connect_component_to(self.components[cidx], self, 'children')
    def set_high_input(self, cidx, port):
        wire = self.components[cidx][port]
        wire.set_high()
        wire.changeable = False
    def set_low_input(self, cidx, port):
        wire = self.components[cidx][port]
        wire.set_low()
        wire.changeable = False
    def reset(self):
        for w in self.get_wires():
            w.disconnect()
    def run(self):
        for lbl in self.inputs.labels:
            self.propagate(self.inputs[lbl])
        components_in_order = self.set_components_in_order_to_run()
        for c in components_in_order:
            c.run()
            for lbl in c.outputs.labels:
                self.propagate(c.outputs[lbl])
    def test_set(self, cases, label_display_order=None):
        """label_order doesn't change the input order for case tests, only visualization"""
        input_labels = self.inputs.labels if label_display_order is None else label_display_order
        indexes = list(self.inputs.labels.index(l) for l in input_labels)
        self._test_header(input_labels)
        for case in cases:
            if len(case) != self.inputs.nrbits: self.error("case with mismatch number of entries.")
            inputs = dict((k, v) for k, v in zip(input_labels, list(case[i] for i in indexes)))
            self.set_input_values(inputs)
            self.run()
            print(' ' + self.inputs.str(', ', order=input_labels) + ' | ' + self.outputs.str(', '))
        print('')


if __name__ == "__main__":
    Not = Gate('Not', 1, ['in'], ['out'])
    Not.set_as_vcc(0, 'C')
    Not.set_as_gnd(0, 'E')
    Not.set_as_input(0, 'B', 'in')
    Not.set_as_output(0, 'C', 'out')
    Not.test_all()
    And = Gate('And', 2, ['a', 'b'], ['z'])
    And.set_as_vcc(0, 'C')
    And.set_as_gnd(1, 'E')
    And.set_as_input(0, 'B', 'a')
    And.set_as_input(1, 'B', 'b')
    And.set_as_output(1, 'E', 'z')
    And.connect(0, 'E', 1, 'C')
    # And.info()
    And.test_all()
    And2 = And.copy()
    And2.test_all()
    Or = Gate('Or', 2, ['a', 'b'], ['z'])
    Or.connect(0, 'C', 1, 'C')
    Or.connect(0, 'E', 1, 'E')
    Or.set_as_vcc(0, 'C')
    Or.set_as_gnd(0, 'E')
    Or.set_as_input(0, 'B', 'a')
    Or.set_as_input(1, 'B', 'b')
    Or.set_as_output(0, 'E', 'z')
    Or2 = Or.copy()
    # Or.info()
    Or2.test_all()
    Nand = Gate('Nand', 2, ['a', 'b'], ['z'])
    Nand.set_as_vcc(0, 'C')
    Nand.set_as_gnd(1, 'E')
    Nand.set_as_input(0, 'B', 'a')
    Nand.set_as_input(1, 'B', 'b')
    Nand.set_as_output(1, 'C', 'z')
    Nand.connect(0, 'E', 1, 'C')
    # Nand.info()
    Nand.test_all()
    Nand2 = Nand.copy()
    Nand2.test_all()
    Nor = Gate('Nor', 2, ['a', 'b'], ['z'])
    Nor.connect(0, 'C', 1, 'C')
    Nor.connect(0, 'E', 1, 'E')
    Nor.set_as_vcc(0, 'C')
    Nor.set_as_gnd(0, 'E')
    Nor.set_as_input(0, 'B', 'a')
    Nor.set_as_input(1, 'B', 'b')
    Nor.set_as_output(0, 'C', 'z')
    # Nor.info()
    Nor.test_all()
    And4 = Gate('And4way', 4, ['a', 'b', 'c', 'd'], ['z'])
    And4.set_as_vcc(0, 'C')
    And4.set_as_gnd(3, 'E')
    And4.set_as_input(0, 'B', 'a')
    And4.set_as_input(1, 'B', 'b')
    And4.set_as_input(2, 'B', 'c')
    And4.set_as_input(3, 'B', 'd')
    And4.set_as_output(3, 'E', 'z')
    And4.connect(0, 'E', 1, 'C')
    And4.connect(1, 'E', 2, 'C')
    And4.connect(2, 'E', 3, 'C')
    And4.test_all()
    Xor = Circuit('Xor', ['a', 'b'], ['z'])
    Xor.add_components(Nand, Or, And)
    Xor.set_as_input(0, 'a', 'a')
    Xor.set_as_input(0, 'b', 'b')
    Xor.set_as_output(2, 'z', 'z')
    Xor.connect(0, 'a', 1, 'a')
    Xor.connect(0, 'b', 1, 'b')
    Xor.connect(0, 'z', 2, 'a')
    Xor.connect(1, 'z', 2, 'b')
    Xor2 = Xor.copy()
    Xor2.test_all()
    # Xor.info()
    Xnor = Circuit('Xnor', ['a', 'b'], ['z'])
    Xnor.add_components(Xor, Not)
    Xnor.set_as_input(0, 'a', 'a')
    Xnor.set_as_input(0, 'b', 'b')
    Xnor.set_as_output(1, 'out', 'z')
    Xnor.connect(0, 'z', 1, 'in')
    Xnor.test_all()

print(lbs('w', 5))
print(lbs('@', 5))
print(lbs('@', 30))