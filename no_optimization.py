import rikudo
from ortools.sat.python import cp_model

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        print({v:self.Value(v) for v in self.__variables})
        print("\n")

    def solution_count(self):
        return self.__solution_count

def custom_generate(a, b, c, t:rikudo.Table):
    rs = rikudo.RikudoSolver(t.nodes, t.axial_distance)
    rs.add_constraints_as_custom(a, b, c)

    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(rs.nodes.values())
    solver.parameters.enumerate_all_solutions = True
    status = solver.Solve(rs.model, solution_printer)

    print("Number of solutions:", solution_printer.solution_count() )

def solve(self):
    solver = cp_model.CpSolver()
    status = solver.Solve(self.model)

    if status == cp_model.OPTIMAL:
        return {k: solver.Value(v) for k, v in self.nodes.items()}

if __name__ == "__main__":

    t = rikudo.Table()

    _a = ((4, 0), (6, 0), (1, 2), (3, 2), (4, 3), (6, 3), (0, 4), (2, 4), (1, 5), (2, 5), (4, 5))
    _b = (15, 18, 10, 33, 30, 22, 6, 36, 3, 1, 25)
    _c = [((3, 0), (3, 1)), ((3, 1), (4, 1)), ((4, 2), (5, 2)), ((2, 3), (1, 4))]

    custom_generate(_a, _b, _c, t)
