import itertools
from enum import Enum
from itertools import combinations, chain, product

# from setuptools.namespaces import flatten
from z3 import *


def test_i_set_up_problem_right(board, regions):
    # iterate through the board and create regions based on colors
    for row in range(len(board)):
        for col in range(len(board[0])):
            color = board[row][col]
            if color not in regions:
                regions[color] = []
            regions[color].append((row, col))

    all_squares = set(product(range(len(board)), repeat=2))
    assert all_squares == set(chain.from_iterable(regions.values()))

    for r1, r2 in combinations(regions.values(), 2):
        assert not set(r1) & set(r2), set(r1) & set(r2)


class StarBattleSolver:

    def __init__(self, board, stars_per_region=1):
        self.solutions = []
        self.stars_per_region = stars_per_region
        self.board = board

    def count_solutions(self):

        size = len(self.board)
        solver = Solver()
        # print(solver.help())
        # solver.set("produce_proofs", True)
        is_star = [[Bool(f's_{i}_{j}') for j in range(size)] for i in range(size)]

        # Constraint 1: N stars per row
        for i in range(size):
            solver.add(Sum([If(is_star[i][j], 1, 0) for j in range(size)]) == self.stars_per_region)

        # Constraint 2: N stars per column
        for j in range(size):
            solver.add(Sum([If(is_star[i][j], 1, 0) for i in range(size)]) == self.stars_per_region)

        # Constraint 3: N stars per region
        # For a given region, you would create a list of cell coordinates.
        # Let's say you have a list of regions, `regions`.
        # for region_cells in regions:


        regions = {}
        region_colors = {}
        for row in range(size):
            for col in range(size):
                color = self.board[row][col]
                if color not in regions:
                    regions[color] = []
            # regions_with_one_color.add(color)
                regions[color].append((row, col))
                region_colors[(row, col)] = color


        # if len(regions[color]) > 1 and color in regions_with_one_color:
        #     regions_with_one_color.remove(color)
        # solver.add(Sum([If(is_star[r][c], 1, 0) for r, c in regions]) == self.stars_per_region)
        for region in regions.keys():
            # print(region)

            for region_cells in [regions[region]]:
                solver.add(Sum([If(is_star[r][c], 1, 0) for r, c in region_cells]) == self.stars_per_region)


        # Constraint 4: No adjacent stars
        for i in range(size):
            for j in range(size):
                for i_offset in [-1, 0, 1]:
                    for j_offset in [-1, 0, 1]:
                        if i_offset == 0 and j_offset == 0:
                            continue
                        ni, nj = i + i_offset, j + j_offset
                        if 0 <= ni < size and 0 <= nj < size:
                            solver.add(Implies(is_star[i][j], Not(is_star[ni][nj])))

        # # make sure each star group
        # print(solver)

        if solver.check() != sat:
            # core = solver.unsat_core()
            # print("Unsatisfiable core:", core)
            # print("Solver failed", solver.statistics())
            return 0, [], None

        count = 0
        stats = solver.statistics()

        solution = []
        rows_values = {}
        while solver.check() == sat and count < 5:
            # print(solver.proof())

            if solver.check() == sat:
                model = solver.model()
                # Extract and print the solution
                for i in range(size):
                    row_str = ""
                    for j in range(size):
                        if model.evaluate(is_star[i][j]):
                            row_str += f"({i + 1},{j + 1}) {region_colors[(i,j)]}\t"

                        # else:
                            # row_str += ". "
                    # print(row_str)
            else:
                print("No solution found.")
            count += 1
            m = solver.model()
            # solution = [(int(str(l).replace("q__", "")) + 1, int(m[l].as_long()) + 1) for l in queens]

            # print(f"Solution:\n{str.strip(solution_str)}")
            # print("Solution:", str(solution))
            # print("is star", is_star)
            not_same = Or(is_star[i][j] != m[is_star[i][j]] for i in range(size) for j in range(size))
            # not_same = Or(flat_stars[i] != m[flat_stars[i]] for i in range(size * self.stars_per_region))
            solver.add(not_same)

            # if count >= 2 and not count_all:
            #     return count, None, None, len(regions_with_one_color) > 0  # Stop after finding the first two solutions


        return count, None, None


class StarBattleBacktrackingSolver:

    def __init__(self, board, stars_per_region=1, count_all=False):
        self.solutions = []
        self.rows = 0
        self.board = board
        self.count_all = count_all
        self.size = len(board)
        self.colorCoords = {}
        # self.star_count_for_color = {}
        # self.star_column_count = {}
        self.has_one_color = False
        self.stars_per_region = stars_per_region
        regions_with_one_color = set()

        for r in range(self.size):
            for c in range(self.size):
                color = board[r][c]
                if color not in self.colorCoords:
                    self.colorCoords[color] = []
                    # self.star_count_for_color[color] = 0
                    regions_with_one_color.add(color)
                self.colorCoords[color].append((r, c))
                if len(self.colorCoords[color]) > 1 and color in regions_with_one_color:
                    regions_with_one_color.remove(color)
        # self.coordsForColor = {}
        self.times = 0
        self.has_one_color = len(regions_with_one_color) > 0
        # for color, coords in self.colorCoords.items():
        #     if len(coords) == 1:
        #         self.has_one_color = True
        # for coord in coords:
        #     self.coordsForColor[coord] = color

        self.initial_board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        # print("Color coords:", self.colorCoords)
        # print("Color coords:", self.coordsForColor)

    def count_solutions(self):
        self.backtrack(0)
        # print("Count all", self.count_all, "Times called is_safe:", self.times, len(self.solutions))
        if len(self.solutions) > 1 and not self.count_all:
            return 2, self.solutions, self.has_one_color
        return len(self.solutions), self.solutions, self.has_one_color

    def backtrack(self, row):
        if row == self.size:
            solution = []
            for r in range(self.size):
                for c in range(self.size):
                    if self.initial_board[r][c] == 1:
                        solution.append((r + 1, c + 1))

            # color_set = set()
            # for r, c in solution:
            #     color_set.add(self.board[r - 1][c - 1])
            # if len(color_set) == len(self.board):
            self.solutions.append(solution)
            #     # print("Found solution:", solution)

            if len(self.solutions) >= 2 and not self.count_all:
                return True  # Stop after finding two solutions if not counting all
            return False

        index_combos = list(itertools.combinations(range(len(self.board)), self.stars_per_region))

        for index_combo in index_combos:
            print(f"Row {row} placing stars at", index_combo)
            if len(index_combo) > 1:
                # check if any two are adjacent
                adjacent = False
                for i in range(len(index_combo) - 1):
                    if index_combo[i + 1] - index_combo[i] == 1:
                        adjacent = True
                        break
                if adjacent:
                    print(f"Row {row} skipping adjacent star placement at", index_combo)
                    continue
            for col in index_combo:
                self.initial_board[row][col] = 1
                # for idx, col in enumerate(index_combo):
                # print(f"Row {row} placing star {idx + 1} at column {col}")
                if self.is_safe(row, col):
                    # print("Setting queen at row", row, "col", col, self.times)
                    self.times += 1
                    # if self.has_queen_in_color_map[self.board[row][col]]:
                    #     continue
                    # self.initial_board[row][col] = 1
                    # self.star_count_for_color[self.board[row][col]] += 1
                    # self.queen_columns.add(col)
                    should_stop = (not self.count_all and len(self.solutions) > 1) or self.backtrack(row + 1)
                    if should_stop:
                        return True
                    self.initial_board[row][col] = 0  # backtrack
                    # self.star_count_for_color[self.board[row][col]] -= 1
                # self.queen_columns.remove(col)
                else:
                    print(f"Row {row} cannot place star at column {col}")
                    # return False
                # self.initial_board[row][col] = 1

        # for col in range(self.size):

        return False

    def is_safe(self, row, col):
        # check not same column
        col_count = 0
        for r in range(row):
            if self.initial_board[r][col] == 1:
                col_count += 1
            if col_count >= self.stars_per_region:
                return False
        #
        # if col in self.queen_columns:
        #     return False

        # check not same diagonal
        diags = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diags:
            r, c = row + dr, col + dc
            if 0 <= r < self.size and 0 <= c < self.size:
                if self.initial_board[r][c] == 1:
                    return False

        # check region constraint

        color = self.board[row][col]
        # if self.star_count_for_color[color] >= self.stars_per_region:
        #     return False
        color_count = 0
        for r, c in self.colorCoords[color]:
            if self.initial_board[r][c] == 1:
                color_count += 1

        if color_count >= self.stars_per_region:
            return False
        return True


class SolverType(Enum):
    OG = 1
    BACKER = 2
    SAT = 3
    HEUR = 4

# def run_solver(board: list[list[str]], solver_type: SolverType, count_all: bool = False, max_solutions: int = 100):
#     if solver_type == SolverType.OG:
#         return MySolver.count_solutions(board, count_all=count_all, max_solutions=max_solutions)
#     if solver_type == SolverType.BACKER:
#         solver = StarBattleBacktrackingSolver(board, count_all=count_all)
#         solution_count, solutions, has_one_color = solver.count_solutions()
#         solution = solutions[0] if solutions is not None and len(solutions) > 0 else None
#         return solution_count, None, solution, has_one_color
#
#     if solver_type == SolverType.HEUR:
#         solver = HeuristicSolver(board, v2_deductions=False)
#         if not solver.is_solved():
#             return 2, None, None, solver.has_single_color
#         return 1, None, solver.get_solution(), solver.has_single_color
#     grid_req = GridReq()
#     grid_req.grid = board
#     # start_time_new = datetime.now()
#     res, solutions, has_single = count_solutions_sat(grid_req, count_all=count_all)
#
#     return res, None, solutions[0] if solutions else None, has_single
