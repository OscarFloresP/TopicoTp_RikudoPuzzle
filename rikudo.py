import networkx as nx
from ortools.sat.python import cp_model
import time

axial_direction_vectors = [
    (+1, 0), (+1, -1), (0, -1), 
    (-1, 0), (-1, +1), (0, +1), 
]

class Hex:
    # Axial Coordinates and Pointy representation
    def __init__(self, q, r):
        self.q = q
        self.r = r
        # for Rikudo
        self.number = None

    def axial(self):
        return (self.q, self.r)

    def axial_to_cube(self):
        s = -self.q -self.r
        return (self.q, self.r, s)

    # Exclusively for Pointy representation
    def to_pixel(self, size):
        x = size * ((3**0.5) * self.q  +  (3**0.5)/2 * self.r)
        y = size * (                            3./2 * self.r)
        return (x, y)

# Specificly made for 36 Rikudo version
class Table:
    def __init__(self):
        self.nodes = self.__generate_table_nodes__()
        self.G = self.__generate_table_graph__()

    def __generate_table_nodes__(self):
        nodes = []

        mid, n = 3, 7
        # first half
        for r in range(n - mid):
            for q in range(mid - r, n):
                # nodes[(q, r)] = Hex(q, r)
                nodes.append( Hex(q, r) )
        # last half
        for r in range(mid + 1, n):
            for q in range(n - (r - mid)):
                # nodes[(q, r)] = Hex(q, r)
                nodes.append( Hex(q, r) )

        return [node for node in nodes if node.axial() != (3, 3)]

    def get_neighbors(self):
        g = nx.Graph()
        [ g.add_edge(hexi.axial(), hexj.axial()) \
            for hexi in self.nodes for hexj in self.nodes \
                if hexi != hexj and self.axial_distance(hexi, hexj) == 1]
        return [edge for edge in g.edges ]
    
    def get_nodes_and_pixels(self, size:int) -> dict:
        return {hex.axial():hex.to_pixel(size) for hex in self.nodes }

    def __generate_table_graph__(self):
        g = nx.Graph()
        [ g.add_node(hex.axial(), pos=hex.to_pixel(1)) for hex in self.nodes ]
        # [ g.add_node(hex.axial(), pos=hex.to_pixel(1)) for hex in self.nodes.values() ]
        return g

    def find_by_k(self, k):
        for hex in self.nodes:
            if hex.axial() != k:
                continue
            return hex

    def draw(self):
        g = self.G.copy()
        g.add_node("RIKUDO", pos=Hex(3, 3).to_pixel(1))
        nx.draw(g, nx.get_node_attributes(g, "pos"), with_labels=True)

    def axial_distance(self, a:Hex, b:Hex):
        return (abs(a.q - b.q) 
            + abs(a.q + a.r - b.q - b.r)
            + abs(a.r - b.r)) / 2


    def generate(self, i):
        rs = RikudoSolver(self.nodes, self.axial_distance)
        rs.add_constraints_as_custom([self.nodes[i].axial()], [1], [])

        return rs.solve()

    def solve(self, ltuples, lvalues, lpairs):
        rs = RikudoSolver(self.nodes, self.axial_distance)
        rs.add_constraints_as_custom(ltuples, lvalues, lpairs)

        return rs.solve()

    def solve_w_heuristics(self, i, ivalue, var_strategy, domain_strategy):
        rs = RikudoSolver(self.nodes, self.axial_distance)
        rs.add_constraints_as_custom([self.nodes[i].axial()], [ivalue], [])

        return rs.solve_w_heuristics(var_strategy, domain_strategy)


class RikudoSolver:
    def __init__(self, t_nodes:list, t_axial_distance):
        # Create model, define variables and define domain
        self.model = cp_model.CpModel()
        self.nodes = { hex.axial(): self.model.NewIntVar(1, 36, "number_of_" + str(hex.axial())) for hex in t_nodes }
        self.t_nodes, self.t_axial_distance = t_nodes, t_axial_distance

    def add_constrains_as_empty(self):
        self.model.AddAllDifferent(self.nodes.values())
        for hexi in self.t_nodes:
            for hexj in self.t_nodes:
                if hexi == hexj:
                    continue
                if self.t_axial_distance(hexi, hexj) > 1:
                    # Declare our intermediate boolean variable.
                    b = self.model.NewBoolVar('b')
                    # If
                    self.model.Add( self.nodes[hexi.axial()] > self.nodes[hexj.axial()] ).OnlyEnforceIf(b)
                    self.model.Add( self.nodes[hexi.axial()] < self.nodes[hexj.axial()] ).OnlyEnforceIf(b.Not())
                    # Then
                    self.model.Add( self.nodes[hexi.axial()] - self.nodes[hexj.axial()] > 1 ).OnlyEnforceIf(b)
                    self.model.Add( -self.nodes[hexi.axial()] + self.nodes[hexj.axial()] > 1 ).OnlyEnforceIf(b.Not())

    def add_constraints_as_custom(self, ltuples, lvalues, lpairs):
        self.add_constrains_as_empty()
        # Set all the known values as a constraint
        for t_axial, v in zip(ltuples, lvalues):
            self.model.Add( self.nodes[t_axial] == v )

        # Set all paired links as a constraint
        for ti_axial, tj_axial in lpairs:
            # Declare our intermediate boolean variable.
            b = self.model.NewBoolVar('b')
            # If
            self.model.Add( self.nodes[ti_axial] > self.nodes[tj_axial] ).OnlyEnforceIf(b)
            self.model.Add( self.nodes[ti_axial] < self.nodes[tj_axial] ).OnlyEnforceIf(b.Not())
            # Then
            self.model.Add( self.nodes[ti_axial] - self.nodes[tj_axial] == 1 ).OnlyEnforceIf(b)
            self.model.Add( -self.nodes[ti_axial] + self.nodes[tj_axial] == 1 ).OnlyEnforceIf(b.Not())

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL:
            return {k: solver.Value(v) for k, v in self.nodes.items()}

    def solve_w_heuristics(self, var_strategy, domain_strategy):
        start_time = time.time()
        self.model.AddDecisionStrategy(self.nodes.values(), var_strategy, domain_strategy)

        solver = cp_model.CpSolver()
        solver.parameters.search_branching = cp_model.FIXED_SEARCH

        solver.parameters.max_time_in_seconds = 10.0
        status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL:
            return (time.time() - start_time)

        
if __name__ == "__main__":
    t = Table()

    heuristics_var = [
                      cp_model.CHOOSE_FIRST, # 0
                      cp_model.CHOOSE_LOWEST_MIN, # 1
                      cp_model.CHOOSE_HIGHEST_MAX, # 2
                      cp_model.CHOOSE_MIN_DOMAIN_SIZE, # 3
                      cp_model.CHOOSE_MAX_DOMAIN_SIZE # 4
                      ]
    heuristics_domain = [
                         cp_model.SELECT_MIN_VALUE, # 0
                         cp_model.SELECT_MAX_VALUE, # 1
                         cp_model.SELECT_LOWER_HALF, # 2
                         cp_model.SELECT_UPPER_HALF # 3
                         ]

    heuristics = [(hv, hd) for hv in heuristics_var for hd in heuristics_domain]

    starters = [(0, 1), (3, 1), (-1, 36), (-4, 36)]


    print(" "*15, end="")
    for s in starters:
        print(str(s) + " "*(15-len(str(s))), end="")
    print()
    for h in heuristics:
        print(str(h) + " "*(15-len(str(h))), end="")
        for s in starters:
            try:
                _ = f"{t.solve_w_heuristics(*s, *h):.7f}"
                print(_ + " "* (15-len(_)), end="")
            except:
                print("MAX REACHED"+ " "*4, end="")
        print()
