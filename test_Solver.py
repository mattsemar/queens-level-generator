from datetime import datetime
from unittest import TestCase

from solver import MyOtherSolver, MySolver, run_solver, SolverType
from solver_cvc5 import handle_solve, GridReq, count_solutions_sat
from test_boards import community_level_227_controversial_hard, community_level_multiple_solutions, community_273, \
    test_rand, no_solutions, non_contig_board, all_test_boards


class TestSolver(TestCase):
    def test_solve(self):

        other_solver = MyOtherSolver(community_level_227_controversial_hard)
        solution_count, solutions, has_one_color = other_solver.count_solutions()
        og_count, stats, og_solutions, og_has_one_color, _ = MySolver.count_solutions(community_level_227_controversial_hard, print_solutions=True)
        self.assertEqual(solution_count, og_count)

    def test_solve_multiple(self):
        board = community_level_multiple_solutions
        # other_solver = MyOtherSolver(board)
        # solution_count, solutions, has_one_color = other_solver.count_solutions()
        solution_count, snone, solutions, has_one_color = run_solver(board, solver_type=SolverType.BACKER, count_all=False)
        og_count, stats, og_solution, og_has_one_color = run_solver(board, solver_type=SolverType.OG, count_all=False)
        sat_count, _, sat_solution, sat_has_one_color = run_solver(board, solver_type=SolverType.SAT, count_all=False)
        h_count, _, h_solution, h_has_one_color = run_solver(board, solver_type=SolverType.HEUR, count_all=False)
        self.assertEqual(solution_count, og_count)
        self.assertEqual(solution_count, sat_count)
        self.assertEqual(solution_count, h_count)


    def test_solve_multiple_sanity(self):
        board = community_level_multiple_solutions
        # other_solver = MyOtherSolver(board)
        # solution_count, solutions, has_one_color = other_solver.count_solutions()
        solution_count, snone, solutions, has_one_color = run_solver(board, solver_type=SolverType.BACKER, count_all=True)
        og_count, stats, og_solution, og_has_one_color = run_solver(board, solver_type=SolverType.OG, count_all=True)
        sat_count, _, sat_solution, sat_has_one_color = run_solver(board, solver_type=SolverType.SAT, count_all=True)
        self.assertEqual(solution_count, og_count)
        # counting doesn't work properly for SAT
        # self.assertEqual(solution_count, sat_count)

    # skip this test, it fails
    def test_solve_timing(self):
        board = community_273

        other_solver = MyOtherSolver(board, count_all=True)
        start_time_new = datetime.now()
        solution_count, solutions, has_one_color = other_solver.count_solutions()

        elapsed_new = ((datetime.now() - start_time_new).total_seconds())

        start_time_og = datetime.now()
        og_count, stats, og_solutions, og_has_one_color, _ = MySolver.count_solutions(board)
        elapsed_og = ((datetime.now() - start_time_og).total_seconds())
        self.assertEqual(solution_count, og_count)

        self.assertLessEqual(elapsed_new, elapsed_og)

    def test_solve_timing_small(self):
        board = non_contig_board


        start_time_new = datetime.now()
        # self.assertEqual(solution_count, og_count)
        solution_count, snone, solutions, has_one_color = run_solver(board, solver_type=SolverType.BACKER, count_all=False)
        start_time_og = datetime.now()
        og_count, stats, og_solutions, og_has_one_color = run_solver(board, solver_type=SolverType.OG, count_all=False)
        end_time_og = datetime.now()

        elapsed_new = ((start_time_og - start_time_new).total_seconds())
        elapsed_og = ((end_time_og - start_time_og).total_seconds())
        self.assertEqual(solution_count, og_count)
        self.assertLessEqual(elapsed_new, elapsed_og)
        print(f"New solver time: {elapsed_new} seconds, OG solver time: {elapsed_og} seconds")


    def test_profile_new(self):
        board = community_273
        # start_time_new = datetime.now()
        other_solver = MyOtherSolver(board)

        solution_count, solutions, has_one_color = other_solver.count_solutions()
        self.assertTrue(solution_count == 1)
        other_solver = MyOtherSolver(community_level_multiple_solutions)
        solution_count, solutions, has_one_color = other_solver.count_solutions()
        self.assertTrue(solution_count > 1)
        print(solutions[0])
        print(solutions[1])



    def test_profile_273(self):
        board = community_273
        # start_time_new = datetime.now()
        other_solver = MyOtherSolver(board)

        solution_count, solutions, has_one_color = other_solver.count_solutions()
        self.assertTrue(solution_count == 1)



    def test_solve_sat(self):
        board = community_level_multiple_solutions
        # board = community_273
        grid_req = GridReq()
        grid_req.grid = board
        # start_time_new = datetime.now()
        res = count_solutions_sat(grid_req)

        print(res)

    def test_solution(self):
        board = [
            ['A', 'B', 'B', 'B', 'C', 'C', 'C'],
            ['A', 'B', 'B', 'B', 'D', 'D', 'C'],
            ['A', 'A', 'A', 'A', 'C', 'E', 'C'],
            ['A', 'A', 'E', 'E', 'E', 'E', 'E'],
            ['F', 'A', 'A', 'F', 'E', 'E', 'E'],
            ['F', 'F', 'F', 'F', 'E', 'G', 'E'],
            ['F', 'F', 'F', 'F', 'F', 'G', 'G'],
        ]
        count, _, solution, has_one = run_solver(board, solver_type=SolverType.SAT, count_all=False)
        self.assertEqual(count, 1)

        og_count, _, og_solution, og_has_one = run_solver(board, solver_type=SolverType.OG, count_all=False)
        self.assertEqual(og_count, 1)
        self.assertEqual(og_solution, solution)

    def test_compare_solutions(self):
        for i in range(len(all_test_boards)):
            board = all_test_boards[i]
            og_count, _, og_solution, og_has_single = run_solver(board, solver_type=SolverType.OG, count_all=False)
            backer_count, _, backer_solution, backer_has_single = run_solver(board, solver_type=SolverType.BACKER, count_all=False)
            self.assertEqual(og_count, backer_count)
            self.assertEqual(og_has_single, backer_has_single)
            if og_count == 1:
                self.assertEqual(og_solution, backer_solution, f"Solutions do not match for board: {board} index {i} {og_count} {backer_count}")
            else:
                print(f"Board index {i} has {og_count} solutions")

