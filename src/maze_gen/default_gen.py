class Generator:
    def __init__(self, size, edges, sln, smt_file, transformations):
        self.size = size
        self.edges = edges
        self.sln = sln

    def get_logic_def(self):
        logic_def = ""
        return logic_def

    def get_logic_c(self):
        logic_c = list()
        for idx in range(self.size):
            logic_c.append("\t\tsigned char c = __VERIFIER_nondet_char();")
        return logic_c

    def get_guard(self):
        guard = list()
        for idx in range(self.size):
            numb_edges = len(self.edges[idx])
            conds = []
            if numb_edges == 1:
                conds = [1]
            elif numb_edges == 2:
                conds = ["c < 0", "c >= 0"]
            elif numb_edges == 3:
                conds = ["c < -43", "c < 42", "c >= 42"]
            elif numb_edges == 4:
                conds = ["c < -64", "c < 0", "c < 64", "c >= 64"]
            guard.append(conds)
        return guard