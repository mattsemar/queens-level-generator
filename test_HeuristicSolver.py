import copy
import itertools
from unittest import TestCase

import test_queens_g
from HeuristicSolver import HeuristicSolver
from queens_board_draw import ImgUtil
from solver import MyOtherSolver
from test_boards import community_level_227_controversial_hard, community_level_229_size_18, \
    board_with_backtracking_needed, test_b_gen, test_rand, community_273, non_contig_board, board, board_heart_13, \
    board_requiring_simulation, board_13_no_heuristic_solve, board_11, board_11_2, board_11_3, board_17, board_13, \
    board_14, community_281, test_sb_3, board_11_xwing


def draw_board_state(solver, name):
    ImgUtil.print_board(solver.solution, normalize=False)
    solved_board = copy.deepcopy(solver.board)
    for row in range(len(solver.solution)):
        for col in range(len(solver.solution[row])):
            val = solver.solution[row][col]
            if val == 'Q':
                solved_board[row][col] = solved_board[row][col] + '_Q'
                # print("Placing queen at", row, col)
            if val == 'X':
                solved_board[row][col] = solved_board[row][col] + '_X'

    print("Solved board:", solved_board)
    # ImgUtil.print_board(solved_board, normalize=False)
    ImgUtil.draw_board(solved_board, name, normalize=False, draw_coords=True)


class TestHeuristicSolver(TestCase):
    def test_solve(self):
        solver = HeuristicSolver(board)
        solver.solve()
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_solve_13_heart(self):
        solver = HeuristicSolver(board_heart_13)
        solver.solve()
        draw_board_state(solver, '13_heart')
        ImgUtil.draw_board(solver.board, '13_raw', normalize=False)
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_solve_13_requires_simulation(self):
        solver = HeuristicSolver(board_requiring_simulation, v2_deductions=True)
        solver.solve()
        # previous this would be considered to require simulation, but with the addition of placing_queen_causes_obvious_conflict
        # we can consider it solvable
        self.assertTrue('simulation' not in solver.get_technique_names())
        # draw_board_state(solver, '13_requires_simulation')
        # ImgUtil.draw_board(solver.board, '13_requires_simulation_raw', normalize=False)
        # ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_solve_13_hard(self):
        solver = HeuristicSolver(board_13_no_heuristic_solve)
        solver.solve()
        # draw_board_state(solver, '13_hard')
        # ImgUtil.draw_board(solver.board, '13_hard_raw', normalize=False)
        # ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_get_steps_for_227(self):
        solver = HeuristicSolver(community_level_227_controversial_hard)
        solver.solve()
        # draw_board_state(solver, '227')
        # ImgUtil.draw_board(solver.board, '227_raw', normalize=False)
        # ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())
        # print( solver.get_solution_steps())
        print(solver.get_solution_steps_playwright())

    def test_get_steps_for_tg(self):
        solver = HeuristicSolver(test_b_gen)
        solver.solve()
        # draw_board_state(solver, '227')
        # ImgUtil.draw_board(solver.board, '227_raw', normalize=False)
        # ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())
        # print( solver.get_solution_steps())
        print(solver.get_solution_steps_playwright())

    def test_compare_v1_vs_v2_steps(self):
        solver_v1 = HeuristicSolver(community_level_227_controversial_hard, v2_deductions=False)
        solver_v2 = HeuristicSolver(community_level_227_controversial_hard, v2_deductions=True)
        solver_v1.solve()
        solver_v2.solve()
        print("Board link", ImgUtil.generate_request_url(solver_v1.board))

        print("v1 techniques", solver_v1.get_technique_names())
        print("v2 techniques", solver_v2.get_technique_names())
        # print( solver.get_solution_steps())
        print(solver_v1.get_solution_steps())
        print(solver_v2.get_solution_steps())

    def test_solve_11(self):
        solver = HeuristicSolver(board_11)
        solver.solve()
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())
        print(solver.difficulty)

    def test_solve_11_2(self):
        solver = HeuristicSolver(board_11_2)
        solver.solve()
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_solve_11_3(self):
        solver = HeuristicSolver(board_11_3)
        solver.solve()
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_solve_17(self):
        solver = HeuristicSolver(board_17)
        solver.solve()
        print(solver.get_solution_steps())
        # ImgUtil.print_board( solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_solve_13(self):
        solver = HeuristicSolver(board_13)
        # solver.solve()
        # 'find_lines', 'find_color_pairs',
        # 'find_single_possibilities__only_one_position_for_color',
        # 'mark_x_for_single_squares', 'find_lines', 'find_single_possibilities__row_contains_only_one_color', 'find_single_possibilities__only_one_position_for_color', 'mark_x_for_single_squares'

        solver.solve()
        if not solver.is_solved():
            progress = solver.test_placing_queen_eliminates_color(print_debug=True)
            print("Progress from test_placing_queen_eliminates_color:", progress)
            draw_board_state(solver, "test_placing_queen_eliminates_color")
        # solver.print_solution()
        # self.assertTrue(solver.is_invalid_state())
        self.assertTrue(solver.is_solved())

    def test_solve_14(self):
        solver = HeuristicSolver(board_14)
        solver.solve()
        # solver.print_solution()
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_color_pairs(self):
        solver = HeuristicSolver(board)
        solver.find_color_ntuples(2)
        self.assertTrue(solver.solution[0][0] == 'X')
        self.assertTrue(solver.solution[0][1] == 'X')
        self.assertTrue(solver.solution[1][1] == 'X')
        self.assertTrue(solver.solution[1][0] == 'X')

        self.assertTrue(solver.solution[0][4] == 'X')
        self.assertTrue(solver.solution[0][5] == 'X')
        self.assertTrue(solver.solution[0][6] == 'X')
        self.assertTrue(solver.solution[1][4] == 'X')
        self.assertTrue(solver.solution[1][5] == 'X')
        self.assertTrue(solver.solution[1][6] == 'X')

        self.assertTrue(solver.solution[0][8] == 'U')
        self.assertTrue(solver.solution[1][8] == 'X')

    def test_find_lines(self):
        solver = HeuristicSolver(board)
        solver.find_color_ntuples(2)
        solver.find_lines()
        self.assertEqual(solver.solution[2],  ['X', 'X', 'U', 'U', 'X', 'X', 'X', 'X', 'X'])
        # ImgUtil.print_board( solver.solution, normalize=False)

    def test_can_place_queen(self):
        solver = HeuristicSolver(board)
        # ImgUtil.print_board(solver.board, normalize=False)
        # ImgUtil.print_board(board, normalize=False)
        self.assertTrue(solver.can_place_queen(0, 0))
        solver.set_queen_position(0, 0)
        # ImgUtil.print_board(solver.solution, normalize=False)
        self.assertFalse(solver.can_place_queen(0, 1))

    def test_column_pair(self):
        solver = HeuristicSolver(board_heart_13)
        solver.find_color_ntuples(3)
        solver.test_placing_queen_eliminates_color()
        solver.mark_x_for_single_squares()
        solver.find_lines()
        solver.test_placing_queen_eliminates_color()
        progress = solver.find_color_ntuples(2)
        self.assertTrue(progress)
        solver.solve()
        ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())

    def test_heuristic_techniques(self):

        test = community_level_227_controversial_hard
        solver = HeuristicSolver(test)
        solver.solve()
        print("Useless techniques", solver.noop_techniques)
        steps = solver.get_solution_steps()
        print(steps)

    def test_heuristic_techniques_281(self):

        test = community_281
        link = ImgUtil.generate_request_url(test)
        print(link)
        solver = HeuristicSolver(test)
        # solver.solution[0][1] = 'X'
        # solver.solution[0][2] = 'X'

        # solver.solution[0][3] = 'X'
        solver.solve()
        # print("Difficulty", solver.difficulty)
        # steps = solver.get_solution_steps_playwright()
        # print(steps)
        steps_soln = solver.get_solution_steps()
        print(steps_soln)

    def test_playwright_script_227(self):

        test = community_level_227_controversial_hard
        solver = HeuristicSolver(test)

        solver.solve()
        steps = solver.get_solution_steps_playwright()
        print(steps)

    def test_playwright_script_rand(self):

        test = test_rand
        solver = HeuristicSolver(test)
        solver.solve()
        steps = solver.get_solution_steps_playwright()
        print(steps)

    def test_playwright_script(self):
        test = community_level_229_size_18
        solver = HeuristicSolver(test)
        solver.solve()
        steps = solver.get_solution_steps_playwright()
        print(steps)

    def test_playwright_script_stop_before_obvious_conflict(self):
        test = community_273
        solver = HeuristicSolver(test, v2_deductions=False)
        solver.solve()
        steps = solver.get_solution_steps_playwright()
        print(steps)

    def test_steps_v1_deductions(self):
        test = community_273
        solver = HeuristicSolver(test, v2_deductions=False)
        solver.solve()
        steps = solver.get_solution_steps()
        print(steps)

    def test_heuristic_techniques_steps(self):

        test = community_level_229_size_18
        solver = HeuristicSolver(test, v2_deductions=True)
        solver.solve()
        # steps = solver.get_solution_steps()
        # print(steps)
        # Techniques used: ['find_lines', 'find_2tuples_with_only_2_possibles', 'find_color_2tuples', 'find_3tuples_with_only_3_possibles', 'find_4tuples_with_only_4_possibles', 'find_color_4tuples', 'find_5tuples_with_only_5_possibles', 'find_6tuples_with_only_6_possibles', 'find_7tuples_with_only_7_possibles', 'find_8tuples_with_only_8_possibles', 'find_lines', 'find_single_possibilities__only_one_position_in_col', 'find_single_possible', 'mark_x_for_single_squares', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_in_row', 'find_single_possibilities__only_one_position_in_row', 'find_single_possibilities__only_one_position_in_row', 'find_single_possibilities__only_one_position_in_col', 'find_single_possibilities__only_one_position_in_col', 'find_single_possibilities__only_one_position_in_col', 'find_single_possibilities__only_one_position_in_col', 'find_single_possible', 'find_lines', 'mark_x_for_single_squares', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_in_row', 'find_lines', 'find_single_possibilities__only_one_position_in_col', 'find_single_possibilities__only_one_position_in_col', 'mark_x_for_single_squares'] difficulty level: 57.0
        print("Useless techniques", solver.noop_techniques)

    def test_difficulty(self):
        tests = [{"board": board, 'expected_difficulty': 8.5},
                 {
                     "board": board_13,
                     'expected_difficulty': 13.0
                 },
                 {
                     "board": board_11,
                     'expected_difficulty': 11.5
                 },
                 {"board": board_17, 'expected_difficulty': 17.0}
                 ]
        for i in range(len(tests)):
            test = tests[i]
            solver = HeuristicSolver(test["board"])
            solver.solve()
            self.assertTrue(solver.is_solved())
            difficulty = solver.difficulty
            print("Calculated difficulty:", difficulty)
            self.assertEqual(test['expected_difficulty'], difficulty)

    def test_simulation_used_unnecessarily(self):
        solver = HeuristicSolver(board_with_backtracking_needed)
        solver.solve()
        self.assertTrue(solver.is_solved())
        self.assertLess( solver.get_technique_names().count('simulate'), 4)
        print(solver.get_solution_steps())
        print("Useless techniques", solver.noop_techniques)

    def test_273(self):
        solver = HeuristicSolver(community_273)
        solver.solve()
        self.assertTrue(solver.is_solved())
        print(solver.get_solution_steps())
        print("Useless techniques", solver.get_solution_steps_html())


    def test_iter(self):

        # Create a list of 9 values (the actual values don't matter for index combinations)
        my_list = [i for i in range(10)]  # Or any other 9 values
        # labels = [chr(ord('A') + i) for i in range(num_regions)]
        # Generate combinations of 3 indexes from the range of 0 to 8 (inclusive)
        # The range(len(my_list)) provides the indexes from 0 to 8
        print(my_list)
        index_combinations = list(itertools.combinations(range(len(my_list)), 3))
        labels = [(chr(ord('A') + i[0]), chr(ord('A') + i[1]), chr(ord('A') + i[2])) for i in index_combinations]
        print(labels)
        for color1, color2, color3 in labels:
            print(f"Combination: {color1}, {color2}, {color3}")
        # board = [[' ' for _ in range(10)] for _ in range(10)]

    def test_non_contig(self):
        solver = HeuristicSolver(non_contig_board)
        coords = solver.get_color_coords('A')
        # self.assertTrue(len(coords) == 7)
        # solver.solve()
        # ImgUtil.print_board(solver.solution, normalize=False)
        # self.assertTrue(solver.is_solved())
        # print(solver.get_solution_steps())

    def test_constrained_box_playwright(self):
        solver = HeuristicSolver(board_11_xwing, simulation_depth=0, v2_deductions=True)

        solver.solve()
        # draw_board_state(solver, '227')
        # ImgUtil.draw_board(solver.board, '227_raw', normalize=False)
        # ImgUtil.print_board(solver.solution, normalize=False)
        self.assertTrue(solver.is_solved())
        # print( solver.get_solution_steps())
        print(solver.get_solution_steps_playwright())

    def test_box_constraint(self):
        solver = HeuristicSolver(board_11_xwing, simulation_depth=0, v2_deductions=True)
        result = solver.find_box_constraint()
        self.assertTrue(result)

        confined = {'B', 'H', 'D', 'E'}
        # Build outer ring cells
        size = len(board_11_xwing)
        outer_ring = set()
        for c in range(size):
            outer_ring.add((0, c))
            outer_ring.add((size - 1, c))
        for r in range(1, size - 1):
            outer_ring.add((r, 0))
            outer_ring.add((r, size - 1))

        corners = {(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)}

        # Corners should be eliminated
        for r, c in corners:
            self.assertEqual(solver.solution[r][c], 'X',
                             f"Corner ({r},{c}) should be eliminated")

        # Non-confined colors on the outer ring should be eliminated
        for r, c in outer_ring:
            color = board_11_xwing[r][c]
            if color not in confined:
                self.assertEqual(solver.solution[r][c], 'X',
                                 f"({r},{c}) color={color} should be eliminated")

        # Confined color cells on the ring (non-corner) should still be unknown
        for r, c in outer_ring:
            color = board_11_xwing[r][c]
            if color in confined and (r, c) not in corners:
                self.assertEqual(solver.solution[r][c], 'U',
                                 f"({r},{c}) color={color} should still be unknown")

    # def test_3_star(self):
    #     solver = HeuristicSolver(test_sb_3, star_count=3)
    #     solver.solve()
    #     self.assertTrue(solver.is_solved())
