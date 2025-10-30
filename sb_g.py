import random
from datetime import datetime
from itertools import product

from HeuristicSolver import HeuristicSolver
from queens_board_draw import ImgUtil
from sb_solver import StarBattleSolver

positions_by_size = {}

def compute_placement_probability(size, num_placed, base_probability=0.58):
    # size * size placements should be impossible
    # we want to start with a 60% chance of placing the first one
    if num_placed <= 2:
        return base_probability

    if num_placed >= size * size:
        return 0.0
    # linear drop from base probability at 2 to 0.1 at size*size
    return base_probability - ((num_placed - 2) * (0.5 / (size * size - 2)))


# @LineProfiler()
def generate_random_sb_board(size, num_stars):
    # we're going to place 1 of each color at an "anchor" position, but we'll ensure the anchors are
    # on their own rows and columns, then fill in the rest randomly
    labels = [chr(ord('A') + i) for i in range(size)]
    board = [[' ' for _ in range(size)] for _ in range(size)]
    # Place one of each label at a random position
    positions = list(product(range(size), range(size)))
    # print(f"Generating board of size {size} with {num_regions} regions", positions)
    random.shuffle(positions)

    used_rows = set()
    used_cols = set()
    labels_remaining = len(labels)
    starting_segments = num_stars - 1
    for position in positions:
        row, col = position
        if row not in used_rows and col not in used_cols:
            board[row][col] = labels[len(labels) - labels_remaining]
            used_rows.add(row)
            used_cols.add(col)
            for seg in range(starting_segments):
                # add additional segments
                tries = 5
                while True and tries > 0:
                    dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                    far_row, far_col = row + dr * 2, col + dc * 2
                    middle_row, middle_col = row + dr, col + dc
                    if 0 <= far_row < size and 0 <= far_col < size and board[far_row][far_col] == ' ' and board[middle_row][middle_col] == ' ':
                        board[middle_row][middle_col] = labels[len(labels) - labels_remaining]
                        board[far_row][far_col] = labels[len(labels) - labels_remaining]
                        break
                    tries -= 1
            labels_remaining -= 1
            if labels_remaining == 0:
                break

    # print(f"Anchors placed at: {[positions[i] for i in range(num_regions)]}")

    # Now we iterate through each empty cell and see how many neighbors it has that are already filled
    # if the cell has 1 filled neighbor, it gets filled with that neighbor's color
    # if there are multiple filled neighbors, it gets filled with a random one of those neighbors
    used_color_count = {label: 1 for label in labels}

    while True:
        row_indexes = list(range(0, size))
        random.shuffle(row_indexes)
        col_indexes = list(range(0, size))
        random.shuffle(col_indexes)

        unset_spots = 0
        for row in row_indexes:
            for col in col_indexes:
                if board[row][col] == ' ':
                    unset_spots += 1
                    # Check neighbors to see if we can fill this spot
                    filled_neighbors = set()
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] != ' ':
                            filled_neighbors.add(board[nr][nc])
                    if filled_neighbors:
                        if len(filled_neighbors) == 1:
                            s = next(iter(filled_neighbors))
                            choices = [s, None]
                            # If there's only one filled neighbor, fill with that color with a smaller chance as the color_count increases
                            # for size = 7, if the number of used colors is 7, we want a 50% chance of expanding

                            desired_placement_probability = compute_placement_probability(size, used_color_count[s], base_probability=0.85)
                            weights = [desired_placement_probability, 1 - desired_placement_probability]
                            # weights = [1 / used_color_count[s], (used_color_count[s]) / (0.5 * size * size)]
                            # print("Weights for", s, "used count", used_color_count[s], "are", weights)
                            choice = random.choices(choices, weights)[0]
                            # if random.random() > (used_color_count[s]) / (0.5 * size * size):

                            if choice is not None:
                                # print(f"Won spot ({row}, {col}) with color {s} (used {used_color_count[s]})",
                                #       1 / used_color_count[s], weights)
                                used_color_count[s] += 1
                                board[row][col] = s
                        else:
                            neighbor_used_count = [used_color_count[fn] for fn in filled_neighbors]
                            weights = [compute_placement_probability(size, nb_used_count, base_probability=0.85) for nb_used_count in neighbor_used_count]
                            choice = random.choices(list(filled_neighbors), weights)[0]
                            used_color_count[choice] += 1
                            board[row][col] = choice


        if unset_spots == 0:
            break

    # ImgUtil.print_board(board)
    return board


def generate_star_battle(size=15, star_count=2, max_boards=5):

    # log more frequently for bigger boards
    log_interval = 1000 - min(size * 75, 900)
    log_interval = round(log_interval)
    print(f"Log interval set to {log_interval} for size {size} logging 1 / {log_interval} attempts")
    num_regions = size
    attempts = 0
    answers = 0
    broken_board_count = 0
    # most_decisions = 0
    # most_conflicts = 0
    most_both = 0
    # track the rate we generate boards with 1 solution
    start_time = datetime.now()
    valid_boards = 0
    # track boards we've already generated
    # generated_boards = set()
    shifted_boards = []
    shifted_boards_added = 0
    zero_to_multiple_ratios = {
        "zero": 0,
        "multiple": 0,
        "one": 0,
    }
    last_log_time = start_time
    while True and valid_boards < max_boards:
        board = generate_random_sb_board(size, star_count)
        if not board:
            broken_board_count += 1
            print(f"broken board {broken_board_count}")
            continue  # Skip if the board is invalid (not enough regions)
        attempts += 1
        # solutions, stats, solution, has_one_color = run_solver(board, solver_type=SolverType.OG, count_all=False, max_solutions=2)
        count, _, _ = StarBattleSolver(board, star_count).count_solutions()
        # solutions, stats, solution, has_one_color = run_solver(board, solver_type=SolverType.SAT, count_all=False)
        # print(solutions, solutions_alt)

        if (datetime.now() - last_log_time).total_seconds() > 5.0:
            last_log_time = datetime.now()
            # rate we generate boards with 1 solution
            current_rate = valid_boards / ((datetime.now() - start_time).total_seconds())
            # rate we've generated valid boards (0, 1 or more solutions)
            attempt_rate = attempts / ((datetime.now() - start_time).total_seconds())
            print(
                f"Most recent solutions={count}, attempts={attempts}. Generation rate unique solutions {current_rate}/s ({answers}). Valid boards: {attempt_rate}/s."
                f" Shifted boards added {shifted_boards_added},"
                f" zero/multiple/one: {zero_to_multiple_ratios},"
                f" current_queue: {len(shifted_boards)}"
                f" time elapsed: {(datetime.now() - start_time).total_seconds():.2f}s"
            )
            if broken_board_count > 0:
                print(
                    f"Broken boards: {broken_board_count} out of {attempts} attempts, {broken_board_count / attempts * 100:.2f}%")
            # if size > 12 and attempts < 300:
            #     ImgUtil.draw_board(board,
            #                        f"sb_size_{size}_attempt_{attempts}_answers_{answers}")
            #     ImgUtil.print_board(board)
        # else:
        #     print("Elapsed", (datetime.now() - last_log_time).total_seconds(), "Attempts", attempts,)
        # if solutions == 0:
        #     print(f"No solutions found")
        #     ImgUtil.print_board(board,)
        if count > 1:
            zero_to_multiple_ratios["multiple"] += 1
        if count == 0:
            zero_to_multiple_ratios["zero"] += 1

        if count == 1:
            # print("Solution", solution)
            valid_boards += 1
            zero_to_multiple_ratios["one"] += 1

            answers += 1
            ImgUtil.draw_board(board,
                               f"sb_size_{size}_attempt_{attempts}_answers_{answers}")
            should_break = answers > 10
            print(
                f"Found a board with 1 solution after {attempts} attempts. Breaking: {should_break} ")
            ImgUtil.print_board(board)
            if should_break:
                ImgUtil.draw_board(board, "final_board")
                # ImgUtil.make_gif([f"output/board_{attempts}.png"])
                break
        # if 10 > count > 3:
            # print(f"Partial {count} solution after {attempts} attempts:")
            # ImgUtil.draw_board(board, f"partial_{size}_attempt_{attempts}_answers_{answers}_decisions_{decisions}")
            # ImgUtil.print_board(board)

