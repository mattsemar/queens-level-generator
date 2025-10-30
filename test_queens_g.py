from unittest import TestCase

from board_util import get_single_cell_regions, has_disconnected_colors
from queens_board_draw import ImgUtil
from queens_generator import compute_placement_probability, expand_single_regions
from solver import MySolver
from test_boards import hard_13_with_one_spot, non_expandable_board, expandable_15, expandable_16


class Test(TestCase):
    def test_compute_placement_probability_even_at_start(self):
        probability = compute_placement_probability(13, 1, 0.567)
        self.assertAlmostEqual(probability, 0.567, places=3)

    def test_compute_placement_probability_event_no_negatives(self):
        for i in range(11, 45):
            probability = compute_placement_probability(13, i)
            if not 0.0 < probability <= 1.0:
                print("Probability out of range for board size 13x", i, ":", probability)
            self.assertTrue(0.0 < probability <= 1.0,
                            f"Probability {probability} for board size 13x{i} is out of range")

    def test_compute_placement_probability_impossible(self):
        probability = compute_placement_probability(3, 9)
        self.assertAlmostEqual(probability, 0.0, places=3)

    def test_expand_single_regions_left(self):
        expanded_board = expand_single_regions(hard_13_with_one_spot)
        for i in range(1, 13):
            if i == 10:
                continue
            self.assertEqual(expanded_board[i], hard_13_with_one_spot[i], f"Row {i} does not match")
        self.assertEqual(['J', 'J', 'H', 'H', 'H', 'H', 'H', 'L', 'L', 'F', 'K', 'K', 'G'], expanded_board[10],
                         "Should have expanded to the left")
        single_regions = get_single_cell_regions(expanded_board)
        self.assertTrue(len(single_regions) == 0)

    def test_expand_single_regions_default_direction_index_1_up(self):
        expanded_board = expand_single_regions(hard_13_with_one_spot, start_direction_index=1)
        for i in range(1, 13):
            if i == 9:
                continue
            self.assertEqual(expanded_board[i], hard_13_with_one_spot[i], f"Row {i} does not match")
        self.assertEqual(['J', 'J', 'H', 'H', 'F', 'H', 'I', 'I', 'L', 'F', 'G', 'K', 'G'], expanded_board[9],
                         "Should have expanded up")
        single_regions = get_single_cell_regions(expanded_board)
        self.assertTrue(len(single_regions) == 0)

    def test_disconnected_board(self):
        board = [
            ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
            ['B', 'B', 'B', 'B', 'D', 'D', 'B', 'B', 'B', 'B', 'E', 'B', 'B'],
            ['B', 'B', 'B', 'C', 'C', 'C', 'C', 'C', 'B', 'B', 'E', 'B', 'B'],
            ['G', 'B', 'C', 'C', 'C', 'C', 'C', 'C', 'B', 'E', 'A', 'E', 'E'],
            ['G', 'B', 'C', 'C', 'C', 'C', 'C', 'C', 'E', 'E', 'A', 'E', 'E'],
            ['G', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'E', 'E', 'F', 'F', 'F'],
            ['G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'E', 'F', 'F', 'F', 'H'],
            ['G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'I', 'I', 'F', 'F', 'H'],
            ['G', 'G', 'G', 'G', 'C', 'C', 'C', 'L', 'I', 'F', 'F', 'F', 'F'],
            ['G', 'G', 'K', 'G', 'C', 'C', 'C', 'L', 'I', 'I', 'F', 'F', 'F'],
            ['G', 'G', 'K', 'G', 'J', 'J', 'J', 'J', 'I', 'I', 'I', 'I', 'I'],
            ['G', 'G', 'G', 'G', 'J', 'J', 'J', 'J', 'I', 'I', 'I', 'I', 'I'],
            ['G', 'G', 'G', 'G', 'J', 'J', 'M', 'M', 'I', 'I', 'I', 'I', 'I'],
        ]
        has_disc = has_disconnected_colors(board)
        self.assertTrue(has_disc)
        board[3][10] = 'E'
        self.assertFalse(has_disconnected_colors(board))


    # down
    def test_expand_single_regions_default_direction_index_2_right(self):
        expanded_board = expand_single_regions(hard_13_with_one_spot, start_direction_index=2)
        for i in range(1, 13):
            if i == 10:
                continue
            self.assertEqual(expanded_board[i], hard_13_with_one_spot[i], f"Row {i} does not match")
        self.assertEqual(['J', 'J', 'H', 'H', 'H', 'H', 'H', 'H', 'L', 'L', 'K', 'K', 'G'], expanded_board[10],
                         "Should have expanded right")
        single_regions = get_single_cell_regions(expanded_board)
        self.assertTrue(len(single_regions) == 0)

    # down
    def test_expand_single_regions_default_direction_index_3_down(self):
        expanded_board = expand_single_regions(hard_13_with_one_spot, start_direction_index=3)
        for i in range(1, 13):
            if i == 11:
                continue
            self.assertEqual(expanded_board[i], hard_13_with_one_spot[i], f"Row {i} does not match")
        self.assertEqual(['J', 'J', 'H', 'H', 'H', 'H', 'H', 'H', 'L', 'F', 'K', 'K', 'G'], expanded_board[10],
                         "Should have expanded down")
        single_regions = get_single_cell_regions(expanded_board)
        self.assertTrue(len(single_regions) == 0)

    def test_non_expandable_board_north_is_expandable_west(self):
        expanded_board = expand_single_regions(non_expandable_board, 1)
        single_regions = get_single_cell_regions(expanded_board)
        self.assertTrue(len(single_regions) > 0)
        expanded_board = expand_single_regions(non_expandable_board, 0)
        srs = get_single_cell_regions(expanded_board)
        self.assertTrue(len(srs) == 0)
        # self.assertEqual(expanded_board, non_expandable_board, "Board should not have changed")

    def test_expand_board_and_check(self):
        for i in range(4):
            expanded_board = expand_single_regions(expandable_15, start_direction_index=i)
            single_regions = get_single_cell_regions(expanded_board)
            self.assertTrue(len(single_regions) == 0, f"Failed to eliminate single regions with direction index {i}")
            count, _, _, _ = MySolver.count_solutions(expanded_board)
            print(f"Solutions for expanded board with direction index {i}: {count}")
            ImgUtil.print_board(expanded_board, normalize=True)

    def test_expand_board_and_check_16(self):
        for i in range(4):
            expanded_board = expand_single_regions(expandable_16, start_direction_index=i)
            single_regions = get_single_cell_regions(expanded_board)
            self.assertTrue(len(single_regions) == 0, f"Failed to eliminate single regions with direction index {i}")
            count, _, _, _ = MySolver.count_solutions(expanded_board)
            print(f"Solutions for expanded board with direction index {i}: {count}")
            ImgUtil.print_board(expanded_board, normalize=True)
