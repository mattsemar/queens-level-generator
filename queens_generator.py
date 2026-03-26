import copy
import random
from datetime import datetime
from itertools import product

from HeuristicSolver import HeuristicSolver
from board_util import get_single_cell_regions, has_disconnected_colors
from queens_board_draw import ImgUtil
from solver import run_solver, SolverType
from vanity_boards import jack_o_13, fl_clover, corners_15

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


def generate_random_board_v2(size, num_regions):
    # different approach, we're going to place 1 of each color at an "anchor" position, then fill in the rest randomly
    labels = [chr(ord('A') + i) for i in range(num_regions)]
    board = [[' ' for _ in range(size)] for _ in range(size)]
    # Place one of each label at a random position
    positions = list(product(range(size), range(size)))
    # print(f"Generating board of size {size} with {num_regions} regions", positions)
    random.shuffle(positions)
    positions = positions[:num_regions]  # Take only the first num_regions positions
    positions.sort(key=lambda x: (x[0], x[1]))  # Sort positions to ensure they are distinct and ordered
    # board[0][0] = labels[0]  # Place the first label at (0, 0)
    for i in range(num_regions):
        row, col = positions[i]
        board[row][col] = labels[i]

    # print(f"Anchors placed at: {[positions[i] for i in range(num_regions)]}")

    # Now we iterate through each empty cell and see how many neighbors it has that are already filled
    # if the cell has 1 filled neighbor, it gets filled with that neighbor's color
    # if there are multiple filled neighbors, it gets filled with a random one of those neighbors
    used_color_count = {label: 1 for label in labels}

    while True:
        unset_spots = 0
        for row in range(size):
            for col in range(size):
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

                            desired_placement_probability = compute_placement_probability(size, used_color_count[s])
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
                            # else:
                                # print(f"Lost spot ({row}, {col}) with color {s} (used {used_color_count[s]})",1 / used_color_count[s], "weights", weights)
                            # Randomly choose one of the filled neighbors to fill this spot
                        else:
                            neighbor_used_count = [used_color_count[fn] for fn in filled_neighbors]
                            # weights = [1 / nb_used_count for nb_used_count in neighbor_used_count]
                            weights = [compute_placement_probability(size, nb_used_count) for nb_used_count in neighbor_used_count]

                            choice = random.choices(list(filled_neighbors), weights)[0]

                            # print("Chose among multiple filled neighbors", filled_neighbors, "weights", weights, choice, "used counts", neighbor_used_count)
                            used_color_count[choice] += 1
                            board[row][col] = choice

        if unset_spots == 0:
            break

    return board


def generate_random_board_v3(size, num_regions):
    # we're going to place 1 of each color at an "anchor" position, but we'll ensure the anchors are
    # on their own rows and columns, then fill in the rest randomly
    labels = [chr(ord('A') + i) for i in range(num_regions)]
    board = [[' ' for _ in range(size)] for _ in range(size)]
    # Place one of each label at a random position
    positions = list(product(range(size), range(size)))
    # print(f"Generating board of size {size} with {num_regions} regions", positions)
    random.shuffle(positions)

    used_rows = set()
    used_cols = set()
    labels_remaining = len(labels)
    for position in positions:
        row, col = position
        if row not in used_rows and col not in used_cols:
            board[row][col] = labels[len(labels) - labels_remaining]
            used_rows.add(row)
            used_cols.add(col)
            labels_remaining -= 1
            if labels_remaining == 0:
                break

    # print(f"Anchors placed at: {[positions[i] for i in range(num_regions)]}")

    # Now we iterate through each empty cell and see how many neighbors it has that are already filled
    # if the cell has 1 filled neighbor, it gets filled with that neighbor's color
    # if there are multiple filled neighbors, it gets filled with a random one of those neighbors
    used_color_count = {label: 1 for label in labels}

    while True:
        unset_spots = 0
        for row in range(size):
            for col in range(size):
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

default_directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
def expand_single_regions(board, start_direction_index=0):
    new_board = copy.deepcopy(board)
    count = {}
    size = len(board)
    single_cell_regions = get_single_cell_regions(board)
    # print("Single regions to expand:", single_cell_regions)
    directions = [default_directions[start_direction_index], default_directions[(start_direction_index + 1) % 4],
                  default_directions[(start_direction_index + 2) % 4], default_directions[(start_direction_index + 3) % 4]]

    for color, coords in single_cell_regions.items():
        r, c = next(iter(coords))
        count[color] = 1
        while True:
            filled = False

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    new_board[nr][nc] = color
                    r, c = nr, nc
                    count[color] += 1
                    filled = True
                    break
            if filled:
                break
        # print(f"Expanded color {color} to {count[color]} cells")
    return new_board


_vanity_cache = {}


def _get_vanity_board(size, template):
    """Pre-compute and cache the processed vanity board, vanity colors, and available positions."""
    cache_key = (size, id(template))
    if cache_key in _vanity_cache:
        return _vanity_cache[cache_key]

    vanity_colors = set()
    vanity_board = copy.deepcopy(template)
    for i in range(len(vanity_board)):
        for j in range(len(vanity_board[i])):
            if vanity_board[i][j] != 'A':
                vanity_colors.add(vanity_board[i][j])
            else:
                vanity_board[i][j] = ' '

    # Pad to target size if needed
    if len(vanity_board) != size or len(vanity_board[0]) != size:
        new_board = [[' ' for _ in range(size)] for _ in range(size)]
        x_offset = (size - len(vanity_board)) // 2
        y_offset = (size - len(vanity_board[0])) // 2
        for row in range(size):
            for col in range(size):
                if 0 <= (row - x_offset) < len(vanity_board) and 0 <= (col - y_offset) < len(vanity_board[0]):
                    new_board[row][col] = vanity_board[row - x_offset][col - y_offset]
        vanity_board = new_board

    # Pre-compute available positions (non-vanity cells)
    available_positions = []
    for r in range(size):
        for c in range(size):
            if vanity_board[r][c] not in vanity_colors:
                available_positions.append((r, c))

    print(f"Vanity board cached: {size}x{size}, {len(vanity_colors)} vanity colors, {len(available_positions)} available positions")
    ImgUtil.print_board(vanity_board)

    result = {
        'board': vanity_board,
        'vanity_colors': vanity_colors,
        'available_positions': available_positions,
    }
    _vanity_cache[cache_key] = result
    return result


def generate_random_board_v2_with_initial(size, num_regions):
    # use the vanity_board as a starting point
    labels = [chr(ord('A') + i) for i in range(num_regions)]
    board = [[' ' for _ in range(size)] for _ in range(size)]

    cached = _get_vanity_board(size, corners_15)
    v_board = cached['board']
    vanity_colors = cached['vanity_colors']
    available_positions = cached['available_positions']

    # Stamp vanity cells into the board upfront
    for r in range(size):
        for c in range(size):
            if v_board[r][c] in vanity_colors:
                board[r][c] = v_board[r][c]

    # Place anchors only on available (non-vanity) positions
    shuffled_available = list(available_positions)
    random.shuffle(shuffled_available)
    anchor_idx = 0
    for i in range(num_regions):
        if labels[i] in vanity_colors:
            continue
        row, col = shuffled_available[anchor_idx]
        board[row][col] = labels[i]
        anchor_idx += 1

    used_color_count = {label: 1 for label in labels}
    tries = 0
    while True:
        unset_spots = 0
        unset_spots_coords = []
        for row in range(size):
            for col in range(size):
                if board[row][col] == ' ':
                    unset_spots += 1

                    unset_spots_coords.append((row, col))
                    # Check neighbors to see if we can fill this spot
                    filled_neighbors = set()
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] != ' ' and board[nr][
                            nc] not in vanity_colors:
                            filled_neighbors.add(board[nr][nc])
                    if filled_neighbors:
                        # Randomly choose one of the filled neighbors to fill this spot
                        if len(filled_neighbors) == 1:
                            s = next(iter(filled_neighbors))
                            choices = [s, None]
                            desired_placement_probability = compute_placement_probability(size, used_color_count[s])
                            weights = [desired_placement_probability, 1 - desired_placement_probability]
                            choice = random.choices(choices, weights)[0]

                            if choice is not None:
                                used_color_count[s] += 1
                                board[row][col] = s
                        else:
                            neighbor_used_count = [used_color_count[fn] for fn in filled_neighbors]
                            weights = [compute_placement_probability(size, nb_used_count) for nb_used_count in
                                       neighbor_used_count]
                            choice = random.choices(list(filled_neighbors), weights)[0]
                            used_color_count[choice] += 1
                            board[row][col] = choice
        tries += 1

        if unset_spots == 0:
            break
        if tries > 1000:
            print(f"Too many tries ({tries}) to fill the board, breaking out. Unset spots: {unset_spots}", unset_spots_coords)
            ImgUtil.print_board(board)
            return None

    return board


# generate_random_board_v2(7, 7)


# Main loop: try random boards until one with 1 solution is found

def generate(size=15, use_vanity=False, draw=True, max_boards=500):
    size = size
    # log more frequently for bigger boards
    log_interval = 1000 - min(size * 75, 900)
    log_interval = round(log_interval)
    print(f"Log interval set to {log_interval} for size {size} logging 1 / {log_interval} attempts")
    num_regions = size
    attempts = 0
    answers = 0
    broken_board_count = 0
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
    while valid_boards < max_boards:
        was_shifted = False
        if len(shifted_boards) > 0 :
            board = shifted_boards.pop()
            was_shifted = True
        elif use_vanity:
            board = generate_random_board_v2_with_initial(size, num_regions)
        else:
            if size >= 15:
                board = generate_random_board_v3(size, num_regions)
            else:
                board = generate_random_board_v2(size, num_regions)

        if not board:
            broken_board_count += 1
            print(f"broken board {broken_board_count}")
            continue  # Skip if the board is invalid (not enough regions)

        attempts += 1
        solutions, stats, solution, has_one_color, _ = run_solver(board, solver_type=SolverType.BACKER, count_all=False, max_solutions=2)
        if has_one_color:
            for i in range(4):
                new_board = expand_single_regions(board, start_direction_index=i)
                single_regions = get_single_cell_regions(new_board)
                if len(single_regions) == 0:
                    if has_disconnected_colors(new_board):
                        # print("Skipping board with disconnected colors after expansion", ImgUtil.print_board(new_board))
                        continue
                    shifted_boards.append(new_board)
                    shifted_boards_added += 1


        # print("stats", stats, "conflicts" in stats.keys)
        conflicts = stats.get_key_value('conflicts') if stats and 'conflicts' in stats.keys() else 0
        decisions = stats.get_key_value('decisions') if stats and 'decisions' in stats.keys() else 0
        score = conflicts + decisions

        if (datetime.now() - last_log_time).total_seconds() > 5.0:
            last_log_time = datetime.now()
            # rate we generate boards with 1 solution
            current_rate = valid_boards / ((datetime.now() - start_time).total_seconds())
            # rate we've generated valid boards (0, 1 or more solutions)
            attempt_rate = attempts / ((datetime.now() - start_time).total_seconds())
            print(
                f"Most recent solutions={solutions}, attempts={attempts}. Generation rate unique solutions {current_rate}/s ({answers}). Valid boards: {attempt_rate}/s."
                f" Shifted boards added {shifted_boards_added},"
                f" zero/multiple/one: {zero_to_multiple_ratios},"
                f" current_queue: {len(shifted_boards)}"
                f" time elapsed: {(datetime.now() - start_time).total_seconds():.2f}s"
            )
            if broken_board_count > 0:
                print(
                    f"Broken boards: {broken_board_count} out of {attempts} attempts, {broken_board_count / attempts * 100:.2f}%")
            if size > 12 and attempts < 300:
                ImgUtil.draw_board(board,
                                   f"size_{size}_attempt_{attempts}_answers_{answers}_conflicts_{conflicts}_decisions_{decisions}")
                ImgUtil.print_board(board)

        if solutions > 1:
            zero_to_multiple_ratios["multiple"] += 1
        if solutions == 0:
            zero_to_multiple_ratios["zero"] += 1

        if solutions == 1:
            valid_boards += 1
            zero_to_multiple_ratios["one"] += 1
            h_solver = HeuristicSolver(board, simulation_depth=0, v2_deductions=True)
            h_solver.solve()
            if not h_solver.is_solved():
                print("Heuristic solver failed to solve")
            else:
                print("Heuristic solver succeeded")
                score = h_solver.difficulty

            print("Board with 1 solution found. Heuristic", score, "Test url",  ImgUtil.generate_request_url(board))
            if most_both < score:  # and decisions > 800:
                print("solution", solution)
                most_both = score
                print(f"New most conflicts: {most_both} for size {size} after {attempts} attempts", conflicts,
                      decisions, "Heuristic difficulty:", h_solver.difficulty)
            elif score > 40:
                ImgUtil.draw_board(board,
                                   f"size_{size}_nonbest_attempt_{attempts}_answers_{answers}_score_{score}_was_shifted_{was_shifted}")
                ImgUtil.print_board(board)
                continue
            else:
                print(
                    f"Skipping drawing board with score {score}, most so far: {most_both}")
                continue

            answers += 1
            ImgUtil.draw_board(board,
                               f"size_{size}_attempt_{attempts}_answers_{answers}_score_{score}_was_shifted_{was_shifted}")
            should_break = answers > 10
            print(
                f"Found a board with 1 solution after {attempts} attempts. Breaking: {should_break} due to conflicts {conflicts} > {size * size / 2}")
            ImgUtil.print_board(board)
            if should_break:
                ImgUtil.draw_board(board, "final_board")
                # ImgUtil.make_gif([f"output/board_{attempts}.png"])
                break
        if 10 > solutions > 3:
            print(f"Partial {solutions} solution after {attempts} attempts:")
            # ImgUtil.draw_board(board, f"partial_{size}_attempt_{attempts}_answers_{answers}_decisions_{decisions}")
            ImgUtil.print_board(board)

