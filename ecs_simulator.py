import pickle
import os
import uuid
# from functools import reduce
from pathlib import Path
import time

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
        self.created_by = Library.cc_by
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


class Bus(Library):
    def __init__(self, nrbits):
        super().__init__('Bus')
        self.nrbits = nrbits
        self.binvec = list(Wire() for _ in range(self.nrbits))
        self.labels = list(reversed(range(self.nrbits))) #@verify
    def __getitem__(self, index):
        return self.binvec[self.labels.index(index)] #@verify
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
    def bin(self, decimal, nrbits):
        if decimal < 0:
            decimal = 2**nrbits + decimal
            if decimal < 2**(nrbits-1):
                decimal += 2**(nrbits-1)
        return self._convert_to_binary(decimal, nrbits)
    def _convert_to_decimal(self, first=0, last=None):
        if last is None: last = len(self.binvec)
        else: last += 1
        decimal = 0
        for n, b in enumerate(reversed(self.binvec[first:last])):
            if b.next:
                decimal += 2**n
        return decimal
    def dec(self, first=0, last=None, signed=True):
        if last is None: last = len(self.binvec)-1
        decimal = self._convert_to_decimal(first, last)
        if self.binvec[first].next and signed: # neg
            decimal = decimal - 2**(last-first+1)
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
        self.vcc = Wire(1, changeable=False, name='VCC')
        self.gnd =Wire(0, changeable=False, name='GND')
        self.inputs = Bus(len(input_labels))
        self.inputs.set_labels(input_labels)
        self.outputs = Bus(len(output_labels))
        self.outputs.set_labels(output_labels)
        self.components = list(Transistor() for _ in range(nrtransistors))
        self.connections = dict((w, set()) for w in self.get_wires())
        self.connections.update({self.vcc: set(), self.gnd: set()})
        self.inverted_outputs = dict((self.outputs[l], False) for l in self.outputs.labels) \
            if nrtransistors > 0 else None
        self.visited = None
    def __getitem__(self, index):
        if type(index) == int or index in self.inputs.labels:
           return self.inputs[index] 
        if type(index) == int or index in self.outputs.labels:
           return self.outputs[index]
    def get_wires(self):
        wires = [self.vcc, self.gnd]
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
            aux = set(wires_dict[w] for w in v)
            acopy.connections[wires_dict[k]] = aux
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
        self.connect_nodes(self.components[idxQ].ports[portQ], self.vcc)
    def set_as_gnd(self, idxQ, portQ):
        self.connect_nodes(self.components[idxQ].ports[portQ], self.gnd)
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
        if origin == self.gnd:
            return True
        self.visited[origin] = True
        for w in self.connections[origin]:
            if not self.visited[w]:
                aux = self._is_short_circuit(w)
                if aux: return True
        return False
    def is_short_circuit(self):
        self._support_to_navigation()
        return self._is_short_circuit(self.vcc)
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
        print('Inputs (in order) :', self.inputs.labels)
        print('Outputs (in order):', self.outputs.labels)
    def _test_header(self, input_labels, output_labels, compact):
        def max_len(list_str):
            return max(list(len(x) for x in list_str))
        def w1pl(input_labels, output_labels, max_char=None):
            if max_char is None:
                max_char = max_len(input_labels + output_labels)
            letters = ''
            for i in range(max_char):
                letters += ' ' + ' '.join(list(c[i]  if i < len(c) else ' ' for c in input_labels)) + ' | '
                letters += ' '.join(list(c[i]  if i < len(c) else ' ' for c in output_labels)) + '\n'
            return letters[:-1]
        print('\n' + self.header())
        if compact:
            labels = w1pl(input_labels, output_labels)
            len_labels = len(labels.split('\n')[0])
        else:
            labels = ' ' + ', '.join(input_labels) + ' | ' + ', '.join(output_labels)
            len_labels = len(labels)
        print('-' + '-'*len_labels)
        print(labels)
        print('-' + '-'*len_labels)
        return len_labels
    def _labels_order(self, label_display_order):
        if label_display_order is None:
            input_labels = self.inputs.labels
            output_labels = self.outputs.labels
        elif type(label_display_order) == tuple:
            input_labels = label_display_order[0] if len(label_display_order[0]) > 0 else self.inputs.labels
            output_labels = label_display_order[1] if len(label_display_order[1]) > 0 else self.outputs.labels
        else:
            input_labels = label_display_order
            output_labels = self.outputs.labels
        return input_labels, output_labels
    def test_all(self, label_display_order=None, compact=False):
        """
        'label_display_order' changes only visualization, not original label ordering;
        in case of only reordering input labels, 'label_display_order' is a list with all labels in desired order;
        in case of reordering both input and output labels, 'label_display_order' is a tuple with two lists, each with respective labels in desired order.
        'compact=True' will print labels each in a single column.
        """
        input_labels, output_labels = self._labels_order(label_display_order)
        len_labels = self._test_header(input_labels, output_labels, compact)
        dimension = len(input_labels)
        min_count, max_count = 0, 1
        counter = [min_count]*dimension
        elapsed = list()
        while True:
            inputs = dict((k, v) for k, v in zip(input_labels, reversed(counter)))
            t = time.time()
            self.set_input_values(inputs)
            self.run()
            elapsed.append(time.time() - t)
            if compact:
                print(' ' + self.inputs.str(' ', order=input_labels) + ' | ' + self.outputs.str(' ', order=output_labels))
            else:
                print(' ' + self.inputs.str(', ', order=input_labels) + ' | ' + self.outputs.str(', ', order=output_labels))
            counter[0] += 1
            for i in range(len(counter)-1):
                if counter[i] > max_count:
                    counter[i] = min_count
                    counter[i+1] += 1
            if counter[-1] > max_count:
                break
        print('-'*len_labels)
        print(f'Mean elapsed time: {sum(elapsed)/len(elapsed)*1000:.2f} ms\n')
    def test_set(self, cases, label_display_order=None, compact=False):
        """
        'cases' MUST respect the original label ordering.
        'label_display_order' doesn't change the input order for case tests, only their visualization;
        in case of only reordering input labels, 'label_display_order' is a list with all labels in desired order;
        in case of reordering both input and output labels, 'label_display_order' is a tuple with two lists, each with respective labels in desired order.
        'compact=True' will print labels each in a single column.
        """
        input_labels, output_labels = self._labels_order(label_display_order)
        indexes = list(self.inputs.labels.index(l) for l in input_labels)
        len_labels = self._test_header(input_labels, output_labels, compact)
        elapsed = list()
        for case in cases:
            if len(case) != self.inputs.nrbits: self.error("case with mismatch number of entries.")
            inputs = dict((k, v) for k, v in zip(input_labels, list(case[i] for i in indexes)))
            t = time.time()
            self.set_input_values(inputs)
            self.run()
            elapsed.append(time.time() - t)
            if compact:
                print(' ' + self.inputs.str(' ', order=input_labels) + ' | ' + self.outputs.str(' ', order=output_labels))
            else:
                print(' ' + self.inputs.str(', ', order=input_labels) + ' | ' + self.outputs.str(', ', order=output_labels))
        print('-'*len_labels)
        print(f'Mean elapsed time: {sum(elapsed)/len(elapsed)*1000:.2f} ms\n')


class Circuit(Gate):
    def __init__(self, name, input_labels, output_labels):
        super().__init__(name, 0, input_labels, output_labels)
        self.circuitry = dict()
        self.new_circuitry_entry(self)
    def new_circuitry_entry(self, key):
        self.circuitry[key] = { 'level': -1, 'same': [], 'children': [] }
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
                    self.prepare_circuitry_levels(key=c, level=level)
        for c in self.circuitry[key]['children']:
            if c != self:
                if self.circuitry[c]['level'] <= level:
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
    def test_arithm(self, compact=True, label_display_order=None, msg = '', unsigned=[], **kwargs):
        def get_prefix(label):
            for i in range(len(label)):
                if label[i].isnumeric():
                    return label[0:i]
            return '' if label.isnumeric() else label
        input_labels, output_labels = self._labels_order(label_display_order)
        input_prefix = list()
        for lbl in input_labels:
            aux = get_prefix(lbl)
            if not aux in input_prefix: input_prefix.append(aux)
        inputs_dict = dict()
        for k, v in kwargs.items():
            if k in input_prefix:
                inputs_dict[k] = dict()
                aux = list(l for l in input_labels if get_prefix(l) == k)
                inputs_dict[k]['labels'] = aux
                inputs_dict[k]['value'] = v
                inputs_dict[k]['nrbits'] = len(aux)
                inputs_dict[k]['idbit'] = self.inputs.binvec.index(self.inputs[aux[0]])
                inputs_dict[k]['signed'] = not k in unsigned
        user_input = ' received inputs (decimal): ' + ', '.join(list(f"{p}={inputs_dict[p]['value']}" for p in input_prefix))
        output_prefix = list()
        for lbl in output_labels:
            aux = get_prefix(lbl)
            if not aux in output_prefix: output_prefix.append(aux)
        outputs_dict = dict()
        for p in output_prefix:
            outputs_dict[p] = dict()
            aux = list(l for l in output_labels if get_prefix(l) == p)
            outputs_dict[p]['labels'] = aux
            outputs_dict[p]['value'] = None
            outputs_dict[p]['nrbits'] = len(aux)
            outputs_dict[p]['idbit'] = self.outputs.binvec.index(self.outputs[aux[0]])
            outputs_dict[p]['signed'] = not p in unsigned
        len_labels = self._test_header(input_labels, output_labels, compact)
        inputs = dict()
        for k in inputs_dict.keys():
            for l, i in zip(inputs_dict[k]['labels'], self.inputs.bin(inputs_dict[k]['value'], inputs_dict[k]['nrbits'])):
                inputs[l] = i
        t = time.time()
        self.set_input_values(inputs)
        self.run()
        elapsed = time.time() - t
        for p in input_prefix:
            idx = inputs_dict[p]['idbit']
            inputs_dict[p]['value'] = self.inputs.dec(idx, idx + inputs_dict[p]['nrbits'] - 1, inputs_dict[p]['signed'])
        for p in output_prefix:
            idx = outputs_dict[p]['idbit']
            outputs_dict[p]['value'] = self.outputs.dec(idx, idx + outputs_dict[p]['nrbits'] - 1, outputs_dict[p]['signed'])
        if compact:
            print(' ' + self.inputs.str(' ', order=input_labels) + ' | ' + self.outputs.str(' ', order=output_labels))
        else:
            print(' ' + self.inputs.str(', ', order=input_labels) + ' | ' + self.outputs.str(', ', order=output_labels))
        print('-'*len_labels)
        print(user_input)
        print(f" operation {'' if msg == '' else '['+msg.upper()+']'} applied to: ",
            ', '.join(list(f"{p}={inputs_dict[p]['value']}" for p in input_prefix)), '| result: ', 
            ', '.join(list(f"{p}={outputs_dict[p]['value']}" for p in output_prefix)))
        print('-'*len_labels)
        print(f'Elapsed time: {elapsed*1000:.2f} ms\n')
