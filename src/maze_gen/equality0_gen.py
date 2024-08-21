import random

class Generator:
    def __init__(self, size, edges, sln, smt_file, transformations):
        self.size = size
        self.edges = edges
        self.sln = sln

    def get_logic_def(self):
        return ""

    def get_logic_c(self):
        logic_c = list()
        for idx in range(self.size):
            logic_c.append("\t\tsigned char c = __VERIFIER_nondet_char();")
        return logic_c

    def get_guard(self):
        guard = list()
        default = [["0"], ["1"],
            ["c < 0", "c >= 0"],
            ["c < -43", "c < 42", "c >= 42"],
            ["c < -64", "c < 0", "c < 64", "c >= 64"]]
        equality = [["0"], ["c == 1"],
            ["c == -64", "c == 64"],
            ["c == -85", "c == 1", "c == 87"],
            ["c == -96", "c == -32", "c == 32", "c == 96"]]
        proportion_eq, total_edges = 0, 0
        for idx in range(self.size):
            total_edges = total_edges + len(self.edges[idx])
        eq_edges = int(total_edges*proportion_eq)
        eq_nodes = set()
        random.seed(0)
        while eq_edges > 0:
            idx = random.randrange(0, self.size)
            if not idx in eq_nodes:
                eq_nodes.add(idx)
                eq_edges = eq_edges - len(self.edges[idx])
        for idx in range(self.size):
            numb_edges = len(self.edges[idx])
            if idx in eq_nodes:
                guard.append(equality[numb_edges])
            else:
                guard.append(default[numb_edges])
        return guard