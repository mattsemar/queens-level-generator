import copy
import random
from datetime import datetime
from itertools import product

from HeuristicSolver import HeuristicSolver
from board_util import get_single_cell_regions, has_disconnected_colors
from queens_board_draw import ImgUtil
from solver import run_solver, SolverType
from vanity_boards import jack_o_13, fl_clover, corners_2

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


v_board_ref = {
    "actual": [],
}


def generate_random_board_v2_with_initial(size, num_regions):
    # use the vanity_board as a starting point
    labels = [chr(ord('A') + i) for i in range(num_regions)]
    board = [[' ' for _ in range(size)] for _ in range(size)]
    # Place one of each label at a random position
    positions = list(product(range(size), range(size)))
    # print(f"Generating board of size {size} with {num_regions} regions", positions)
    random.shuffle(positions)
    # make sure postion (0, 0) is at the start
    # if positions[0] != (0, 0) :
    #     old_pos = positions[0]
    #     positions[0] = (0, 0)
    #     print("swapping (0, 0) with", old_pos)
    #     positions[positions.index((0, 0))] = old_pos
    truncated_positions = positions[:num_regions]  # Take only the first num_regions positions
    truncated_positions.sort(key=lambda x: (x[0], x[1]))  # Sort positions to ensure they are distinct and ordered

    # board[truncated_positions[0][0]][truncated_positions[0][1]] = labels[0]  # Place the first label at (0, 0)
    extra_positions_used = set()
    vanity_colors = set()

    # new convention is that vanity boards must use As as blank spots and other letters as vanity colors
    vanity_board = copy.deepcopy(corners_2)
    for i in range(len(vanity_board)):
        for j in range(len(vanity_board[i])):
            if vanity_board[i][j] != 'A':
                vanity_colors.add(vanity_board[i][j])
            else:
                vanity_board[i][j] = ' '

    if len(v_board_ref['actual']) == 0:
        v_board_ref['actual'] = vanity_board
        new_board = [[' ' for _ in range(size)] for _ in range(size)]

        x_offset = (size - len(
            v_board_ref['actual'])) // 2  # how far left to go when picking up stuff from template board
        y_offset = (size - len(v_board_ref['actual'][0])) // 2  # how far up/down
        for row in range(size):
            for col in range(size):
                if 0 <= (col - x_offset) < len(v_board_ref['actual']) and 0 <= (row - y_offset) < len(
                        v_board_ref['actual'][0]):
                    print("Setting position", "row", row, "col", col, "to",
                          v_board_ref['actual'][col - x_offset][row - y_offset])
                    new_board[row][col] = v_board_ref['actual'][row - x_offset][col - y_offset]

        v_board_ref['actual'] = new_board
        print(f"Vanity board after padding: {len(v_board_ref['actual'])}x{len(v_board_ref['actual'][0])}")
        # raise Exception("Padding not supported yet")

        ImgUtil.print_board(v_board_ref['actual'])
        # ImgUtil.draw_board(v_board_ref['actual'], "expanded vanity_board_fork")

    v_board = v_board_ref['actual']

    # vanity_board_201 = v_board

    for i in range(num_regions):
        if labels[i] in vanity_colors:
            continue
        row, col = truncated_positions[i]
        if v_board[row][col] not in vanity_colors:
            board[row][col] = labels[i]
        else:
            # need to find a new position
            found_spot = False
            while True and not found_spot:
                # print(f"Trying to find a new position for label {labels[i + 1]} at index {i + 1}, current position: ({row}, {col})")
                for j in range(num_regions, len(positions)):
                    if j in extra_positions_used:
                        # print(f"Skipping position {j} as it has already been used")
                        continue
                    r, c = positions[j]
                    if v_board[r][c] not in vanity_colors:
                        board[r][c] = labels[i]
                        extra_positions_used.add(j)
                        found_spot = True
                        break

                if not found_spot:
                    print(f"Could not find a new position for label {labels[i]}, trying again")
                    row, col = random.choice(positions)
                    if v_board[row][col] not in vanity_colors:
                        board[row][col] = labels[i]
                        found_spot = True
                    else:
                        print(f"Position ({row}, {col}) is already taken by a vanity color, trying again")

    for i in range(size):
        for j in range(size):
            if v_board[i][j] in vanity_colors:
                board[i][j] = v_board[i][j]

    used_color_count = {label: 1 for label in labels}
    tries = 0
    while True:
        unset_spots = 0
        unset_spots_coords = []
        for row in range(size):
            for col in range(size):
                if v_board[row][col] in vanity_colors:
                    board[row][col] = v_board[row][col]
                elif board[row][col] == ' ':
                    unset_spots += 1

                    unset_spots_coords.append((row, col))
                    # print(f"Unset spot at ({row}, {col})")
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
        # print(f"Used color counts: {used_color_count}m Unset spots: {unset_spots}")

    # ImgUtil.print_board(board)
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
        solutions, stats, solution, has_one_color = run_solver(board, solver_type=SolverType.OG, count_all=False, max_solutions=2)
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
        # solutions = count_solutions(board, count_all=attempts % 100 == 0)
        # print("Attempt", attempts, "found", solutions, "solutions with conflicts", conflicts, "decisions",)
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
        # else:
        #     print("Elapsed", (datetime.now() - last_log_time).total_seconds(), "Attempts", attempts,)
        # if solutions == 0:
        #     print(f"No solutions found")
        #     ImgUtil.print_board(board,)
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
                # if "simulation" in h_solver.get_technique_names():
                #     score = 0
                #     print("Setting score to 0 due to simulation technique required")
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

