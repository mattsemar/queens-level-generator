from unittest import TestCase

from sb_solver import StarBattleSolver, StarBattleBacktrackingSolver
from test_boards import community_level_227_controversial_hard


class TestStarBattleBacktrackingSolver(TestCase):

    def test_solve_queens(self):

        other_solver = StarBattleBacktrackingSolver(community_level_227_controversial_hard, stars_per_region=1)
        solution_count, solutions, has_one_color = other_solver.count_solutions()
        # og_count, stats, og_solutions, og_has_one_color = MySolver.count_solutions(community_level_227_controversial_hard)
        self.assertEqual(solution_count, 1)
        # Solution: [(1, 11), (2, 2), (3, 4), (4, 7), (5, 5), (6, 3), (7, 9), (8, 1), (9, 8), (10, 10), (11, 6)]

    def test_simple_backtracking_solver(self):
        sb_board = [
            ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'K', 'K', 'K'],
            ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'K', 'K'],
            ['H', 'H', 'C', 'C', 'H', 'G', 'G', 'E', 'H', 'K', 'K', 'K'],
            ['H', 'H', 'C', 'C', 'G', 'G', 'G', 'E', 'E', 'E', 'K', 'K'],
            ['H', 'C', 'C', 'C', 'C', 'G', 'G', 'G', 'E', 'E', 'K', 'E'],
            ['C', 'C', 'C', 'I', 'I', 'I', 'G', 'G', 'E', 'E', 'E', 'E'],
            ['I', 'I', 'I', 'I', 'I', 'D', 'D', 'D', 'E', 'F', 'E', 'E'],
            ['I', 'I', 'A', 'I', 'I', 'D', 'D', 'D', 'F', 'F', 'F', 'E'],
            ['L', 'L', 'A', 'A', 'A', 'A', 'D', 'D', 'F', 'F', 'F', 'F'],
            ['L', 'L', 'A', 'A', 'D', 'D', 'D', 'B', 'B', 'F', 'F', 'F'],
            ['L', 'L', 'L', 'L', 'B', 'B', 'B', 'B', 'J', 'J', 'F', 'F'],
            ['L', 'L', 'L', 'L', 'J', 'J', 'J', 'J', 'J', 'J', 'J', 'F'],
        ]


        solver = StarBattleBacktrackingSolver(sb_board, stars_per_region=2)
        soln_count, solutions, has_one = solver.count_solutions()


        print(solutions)
        self.assertEqual(1, soln_count, "Solver's solution does not match expected solution")


class TestStarBattleZ3Solver(TestCase):

    def test_solve_queens(self):

        z3_solver = StarBattleSolver(community_level_227_controversial_hard, stars_per_region=1)
        solution_count, solutions, has_one_color = z3_solver.count_solutions()
        # og_count, stats, og_solutions, og_has_one_color = MySolver.count_solutions(community_level_227_controversial_hard)
        self.assertEqual(solution_count, 1)
        # Solution: [(1, 11), (2, 2), (3, 4), (4, 7), (5, 5), (6, 3), (7, 9), (8, 1), (9, 8), (10, 10), (11, 6)]

    def test_z3(self):
        sb_board = [
            ['G', 'G', 'G', 'G', 'G', 'G', 'C', 'F', 'F', 'F'],
            ['E', 'E', 'E', 'G', 'G', 'G', 'C', 'F', 'F', 'F'],
            ['E', 'G', 'G', 'G', 'G', 'G', 'C', 'C', 'F', 'F'],
            ['E', 'G', 'A', 'G', 'G', 'J', 'J', 'J', 'J', 'J'],
            ['H', 'A', 'A', 'G', 'G', 'J', 'D', 'I', 'J', 'J'],
            ['H', 'A', 'H', 'J', 'J', 'J', 'D', 'I', 'J', 'J'],
            ['H', 'H', 'H', 'J', 'J', 'J', 'D', 'I', 'J', 'J'],
            ['H', 'B', 'H', 'J', 'J', 'D', 'D', 'I', 'I', 'I'],
            ['B', 'B', 'H', 'H', 'H', 'D', 'H', 'I', 'I', 'I'],
            ['B', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'I', 'I'],        ]

        solver = StarBattleSolver(sb_board, stars_per_region=2)
        soln_count, solutions, has_one = solver.count_solutions()


        print(solutions)
        self.assertEqual(1, soln_count, "Solver's solution does not match expected solution")
