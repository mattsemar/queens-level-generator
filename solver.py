from enum import Enum

from itertools import combinations, chain, product

from z3 import *

from HeuristicSolver import HeuristicSolver
from sb_solver import StarBattleSolver


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


def pad_number(n, width):
    s = str(n)
    while len(s) < width:
        s = ' ' + s
    return s


class MySolver:

    def __init__(self, board):
        self.solutions = []
        self.rows = 0
        self.board = board
        # self.ivs

    @classmethod
    # @LineProfiler()
    def count_solutions(cls, board, count_all=False, constrain_one_q=False, constrained_q_row=None,
                        constrained_q_col=None, print_solutions=False, max_solutions=100, star_count=1):
        if star_count > 1:
            count = StarBattleSolver(board, stars_per_region=star_count).count_solutions()
            return count, None, None, None, []

        size = len(board)
        context = Context()
        # print("Context:", context)
        # Create a solver instance
        solver = Solver(ctx=context)
        # queens[n] = col of queen on row n
        # by construction, not on same row
        queens = IntVector('q', size, ctx=context)
        solver.add([And(0 <= i, i < size) for i in queens])
        solver.add(Distinct(queens))  # all queens must be in different columns

        # not diagonally adjacent
        for i in range(size - 1):
            q1, q2 = queens[i], queens[i + 1]
            solver.add(Abs(q1 - q2) != 1)

        regions = {}
        regions_with_one_color = set()
        for row in range(size):
            for col in range(size):
                color = board[row][col]
                if color not in regions:
                    regions[color] = []
                    regions_with_one_color.add(color)
                regions[color].append((row, col))
                if len(regions[color]) > 1 and color in regions_with_one_color:
                    regions_with_one_color.remove(color)

        # test_i_set_up_problem_right(board, regions)

        for r in regions.values():
            # print("Region:", r)
            solver.add(Or(
                *[queens[row] == col for (row, col) in r]
            ))

        if solver.check() != sat:
            return 0, None, None, len(regions_with_one_color) > 0, []

        count = 0
        stats = solver.statistics()

        solution = []
        all_solutions = []
        rows_values = {}
        while solver.check() == sat:
            count += 1
            m = solver.model()

            solution = [(int(str(l).replace("q__", "")) + 1, int(m[l].as_long()) + 1) for l in queens]
            all_solutions.append(solution)
            solution_str = [(pad_number(int(str(l).replace("q__", "")) + 1, 2), pad_number((int(m[l].as_long()) + 1), 2))
                        for l in queens]
            for l in queens:
                cur_row = int(str(l).replace("q__", "")) + 1
                cur_col = int(str(m[l].as_long())) + 1
                if cur_row not in rows_values:
                    rows_values[cur_row] = set()
                rows_values[cur_row].add(cur_col)
                # if cur_row == 1:
                #     print(f"Row {cur_row } has possible column {cur_col } {rows_values[cur_row]}")
                # rows_values.append((int(str(l).replace("q__", "")) + 1, int(m[l].as_long()) + 1))
            if print_solutions:
                print("Solution:", str(solution_str).replace("'", ""))

            not_same = Or(queens[i] != m[queens[i]] for i in range(size))
            solver.add(not_same)

            # if count >= 2 and not count_all:
            #     return count, None, None, len(regions_with_one_color) > 0  # Stop after finding the first two solutions
            if count >= max_solutions and not count_all:
                if print_solutions:
                    card = 0
                    for r in rows_values.keys():
                        if len(rows_values[r]) == 1:
                            card += 1
                            print(f"Row {r} has fixed column {rows_values[r]}")
                        else:
                            card += len(rows_values[r])
                            print(
                                f"Row {r} has multiple columns {len(rows_values[r])} {sorted(rows_values[r])}")
                    print(f"Cardinality score {card / size}")
                return count, None, None, len(regions_with_one_color) > 0, all_solutions

        if count > 1:
            if print_solutions:
                # print which values are fixed
                card = 0
                for r in rows_values.keys():
                    if len(rows_values[r]) == 1:
                        card += 1
                        print(f"Row {r} has fixed column {rows_values[r]}")
                    else:
                        card += len(rows_values[r])
                        print(
                            f"Row {r} has multiple columns {len(rows_values[r])} {sorted(rows_values[r])}")
                print(f"Cardinality score {card / size}")
        if count == 1 and solution:
            if constrain_one_q and (constrained_q_row is not None and constrained_q_col is not None):
                if solution[constrained_q_row] == (constrained_q_row + 1, constrained_q_col + 1):
                    print("Solution with constraint:", solution)
            return count, stats, solution, len(regions_with_one_color) > 0, all_solutions
        return count, None, None, len(regions_with_one_color) > 0, all_solutions


class MyOtherSolver:

    def __init__(self, board, count_all=False):
        self.solutions = []
        self.rows = 0
        self.board = board
        self.count_all = count_all
        self.size = len(board)
        self.colorCoords = {}
        self.has_queen_in_color_map = {}
        self.queen_columns = set()
        self.has_one_color = False
        regions_with_one_color = set()

        for r in range(self.size):
            for c in range(self.size):
                color = board[r][c]
                if color not in self.colorCoords:
                    self.colorCoords[color] = []
                    self.has_queen_in_color_map[color] = False
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

        for col in range(self.size):
            if self.is_safe(row, col):
                # print("Setting queen at row", row, "col", col, self.times)
                self.times += 1
                # if self.has_queen_in_color_map[self.board[row][col]]:
                #     continue
                self.initial_board[row][col] = 1
                self.has_queen_in_color_map[self.board[row][col]] = True
                self.queen_columns.add(col)
                should_stop = (not self.count_all and len(self.solutions) > 1) or self.backtrack(row + 1)
                if should_stop:
                    return True
                self.initial_board[row][col] = 0  # backtrack
                self.has_queen_in_color_map[self.board[row][col]] = False
                self.queen_columns.remove(col)

        return False

    def is_safe(self, row, col):
        # check not same column
        # for r in range(row):
        #     if self.initial_board[r][col] == 1:
        #         return False
        #
        if col in self.queen_columns:
            return False

        # check not same diagonal
        diags = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diags:
            r, c = row + dr, col + dc
            if 0 <= r < self.size and 0 <= c < self.size:
                if self.initial_board[r][c] == 1:
                    return False

        # check region constraint

        color = self.board[row][col]
        if self.has_queen_in_color_map[color]:
            return False
        # for r, c in self.colorCoords[color]:
        #     if self.initial_board[r][c] == 1:
        #         return False

        return True


class SolverType(Enum):
    OG = 1
    BACKER = 2
    SAT = 3
    HEUR = 4


def run_solver(board: list[list[str]], solver_type: SolverType, count_all: bool = False, max_solutions: int = 100):
    if solver_type == SolverType.OG:
        return MySolver.count_solutions(board, count_all=count_all, max_solutions=max_solutions)
    if solver_type == SolverType.BACKER:
        solver = MyOtherSolver(board, count_all=count_all)
        solution_count, solutions, has_one_color = solver.count_solutions()
        solution = solutions[0] if solutions is not None and len(solutions) > 0 else None
        return solution_count, None, solution, has_one_color, solutions if solutions else []

    if solver_type == SolverType.HEUR:
        solver = HeuristicSolver(board, v2_deductions=False)
        if not solver.is_solved():
            return 2, None, None, solver.has_single_color
        return 1, None, solver.get_solution(), solver.has_single_color
    grid_req = GridReq()
    grid_req.grid = board
    # start_time_new = datetime.now()
    res, solutions, has_single = count_solutions_sat(grid_req, count_all=count_all)

    return res, None, solutions[0] if solutions else None, has_single
