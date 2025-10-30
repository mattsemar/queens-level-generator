import copy
import itertools
import traceback

from typing import List, Tuple

# python constant
UNKNOWN_VALUE = 'U'
KNOWN_EMPTY = 'X'
KNOWN_QUEEN = 'Q'


class HeuristicTechnique:
    def __init__(self, name, difficulty=0.0, description="", known_empties_marked=None, queens_placed=None, color=None,
                 descriptions=None):
        self.name = name
        self.difficulty = difficulty
        self.known_empties_marked: List[
            Tuple[int, int]] = known_empties_marked if known_empties_marked is not None else []
        self.queens_placed: List[Tuple[int, int]] = queens_placed if queens_placed is not None else []
        # add 1 to every row column to convert from 0-based to 1-based indexing
        self.queens_placed = [(r + 1, c + 1) for (r, c) in self.queens_placed]
        self.known_empties_marked = [(r + 1, c + 1) for (r, c) in self.known_empties_marked]
        self.description = description
        self.descriptions = descriptions if descriptions is not None else []
        self.color = color

    def __str__(self):
        # return super().__str__()
        return f"HeuristicTechnique(name={self.name}, difficulty={self.difficulty}, known_empties_marked={self.known_empties_marked}, queens_placed={self.queens_placed}, description={self.description})"


class HeuristicSolver:

    def __init__(self, board, simulation_depth=0, v2_deductions=True, star_count = 1):
        self.solution = copy.deepcopy(board)
        self.board = copy.deepcopy(board)
        self.simulation_mode = simulation_depth > 0
        self.simulation_depth = 0
        self.star_count = star_count
        color_counts = {}
        single_colors = set()
        for r in range(len(board)):
            for c in range(len(board[r])):
                self.solution[r][c] = UNKNOWN_VALUE
                self.board[r][c] = board[r][c]
                if board[r][c] not in color_counts:
                    color_counts[board[r][c]] = 0
                color_counts[board[r][c]] += 1
                if color_counts[board[r][c]] == 1:
                    single_colors.add(board[r][c])
                elif board[r][c] in single_colors:
                    single_colors.remove(board[r][c])

        self.has_single_color = len(single_colors) > 0
        self.size = len(board)
        self.colors = [chr(ord('A') + i) for i in range(self.size)]
        self.techniques_used: List[HeuristicTechnique] = []
        self.noop_techniques: List[str] = []
        self.techniques = [
            #  ['mark_x_for_single_squares', 'find_single_possible', 'find_lines', 'find_2tuples_with_only_2_possibles', 'find_color_2tuples', 'find_3tuples_with_only_3_possibles', 'placing_queen_eliminates_color', 'placing_queen_causes_obvious_conflict', 'mark_x_for_single_squares', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_for_color', 'find_single_possible', 'mark_x_for_single_squares', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_for_color', 'find_single_possibilities__only_one_position_for_color'] difficulty level: 16
            self.mark_x_for_single_squares,
            self.find_single_possibilities,
            self.do_find_lines,
            self.find_color_ntuples_iter,
            self.find_ntuples_with_only_n_possibles_iter,

            # self.find_ntuples_with_only_3_possibles,
            # self.find_ntuples_with_only_4_possibles,
            # self.find_ntuples_with_only_5_possibles,
            # self.find_ntuples_with_only_6_possibles,
            # self.find_ntuples_with_only_7_possibles,
            # self.find_ntuples_with_only_8_possibles,
            # self.find_color_2tuples,
            # self.find_color_3tuples,
            # self.find_color_4tuples,
            # self.find_color_5tuples,
            # self.find_color_6tuples,
            # self.find_color_7tuples,
            # self.find_color_8tuples,
            # self.find_color_9tuples,
            # self.find_color_10tuples,
            # self.find_color_11tuples,
            # self.find_color_11tuples,
            self.test_placing_queen_eliminates_color,
            # self.assuming_no_queen_causes_conflict,
            #
            self.test_placing_queen_causes_obvious_conflict,
            self.simulate,
        ]
        self.attempts = 0
        self.difficulty = 0
        self.v2_deductions = v2_deductions
        self.ntuple_checks_run = False

    def solve(self):
        while not self.is_solved():
            made_progress = self.make_deductions()
            self.attempts += 1
            if not made_progress:
                # No further deductions can be made, break to avoid infinite loop
                break
        self.difficulty = sum([t.difficulty for t in self.techniques_used])
        if not self.is_solved():
            self.difficulty *= -1
        print("Techniques used:", self.get_technique_names(), "difficulty level:", self.difficulty)

    def get_solution_steps(self, start_step=1, extra_padding="", step_prefix=""):
        result = ""
        for i in range(start_step, len(self.techniques_used) + 1):
            technique = self.techniques_used[i - 1]
            color_str = f"(color={technique.color}) " if technique.color is not None else ""
            action = "PLACE QUEEN" if len(technique.queens_placed) > 0 else "MARK X"
            coords = technique.queens_placed if len(technique.queens_placed) > 0 else technique.known_empties_marked
            coords_str = "\n\t\t".join([
                f"{extra_padding}( {coords[i][1]:>2d}, {coords[i][0]:>2d},  {self.board[coords[i][0] - 1][coords[i][1] - 1]}) \t{technique.descriptions[i] if len(technique.descriptions) == len(coords) else None}"
                for i in range(len(coords))])
            result += f"{extra_padding}{step_prefix}Step: {i}) [ACTION={action}] ({technique.name}) {color_str}\n\t\t{coords_str} \t {technique.description}\n\n"
        return result

    def get_solution_steps_html(self):
        result = "<div><ol>"

        for i in range(1, len(self.techniques_used) + 1):
            technique = self.techniques_used[i - 1]
            color_str = f"(color={technique.color}) " if technique.color is not None else ""
            action = "PLACE QUEEN" if len(technique.queens_placed) > 0 else "MARK X"
            coords = technique.queens_placed if len(technique.queens_placed) > 0 else technique.known_empties_marked
            coords_str = "\n\t\t".join([
                f"( {coords[i][1]:>2d}, {coords[i][0]:>2d},  {self.board[coords[i][0] - 1][coords[i][1] - 1]}) \t{technique.descriptions[i] if len(technique.descriptions) == len(coords) else None}"
                for i in range(len(coords))])
            # coords = copy.deepcopy(coords)

            # coords = [(r + 1, c + 1) for (r, c) in coords]  # convert to 1-based indexing
            result += f"<li>Step: {i}) [ACTION={action}] ({technique.name}) {color_str}</li>\n"
            result += f"<ol>"
            for coord in coords:
                r, c = coord
                color = self.board[r - 1][c - 1]
                desc = technique.descriptions[coords.index(coord)] if len(technique.descriptions) == len(coords) else ""
                result += f"<li>( {c:>2d}, {r:>2d},  {color}) \t{desc}</li>"

            result += "</ol>"
        result += "</ol></div>"

        # result += f"Step: {i}) [ACTION={action}] ({technique.name}) {color_str}\n\t\t{coords_str} \t {technique.description}\n\n"
        return result

    def get_solution_steps_playwright(self):
        result = """
          const browser = await chromium.launch({ headless: false });
          const context = await browser.newContext({});
          const page = await context.newPage();

          // The actual interesting bit
          await page.goto('http://localhost:3000/community-level/229');\n
          await page.waitForLoadState("domcontentloaded");
"""
        # await page.locator('div:nth-child(37)').click();

        for technique in self.techniques_used:
            # technique = self.techniques_used[i-1]
            # color_str = f"(color={technique.color}) " if technique.color is not None else ""
            action = "PLACE QUEEN" if len(technique.queens_placed) > 0 else "MARK X"
            # coords = technique.queens_placed if len(technique.queens_placed) > 0 else technique.known_empties_marked
            # coords_str = "\n\t\t".join([f"( {coords[i][1]:>2d}, {coords[i][0]:>2d},  {self.board[coords[i][0]-1][coords[i][1]-1]}) \t{technique.descriptions[i] if len(technique.descriptions) == len(coords) else None}" for i in range(len(coords))])
            # coords = copy.deepcopy(coords)
            if action == "PLACE QUEEN":
                for (r, c) in technique.queens_placed:
                    # result += f"await page.locator('css=[data-row=\"{r-1}\"][data-col=\"{c-1}\"]').dblclick(); // {action} ({c} , {r}) {technique.name} \n"
                    result += f"await markQueen(page, {r - 1}, {c - 1}); // Place queen at ({c} , {r}) {technique.name}\n"
                    # result += f"await page.locator('css=[data-row=\"{r-1}\"][data-col=\"{c-1}\"]').dblclick(); // {action} ({c} , {r}) {technique.name} \n"
                    # result += f"await page.locator('div:nth-child({(r - 1) * self.size + c})').click();\n"
                    # result += f"await page.locator('div:nth-child({(r - 1) * self.size + c})').click();\n"
            else:
                for (r, c) in technique.known_empties_marked:
                    # result += f"await page.locator('div:nth-child({(r - 1) * self.size + c})').click();\n"
                    # result += f"await page.locator('css=[data-row=\"{r - 1}\"][data-col=\"{c - 1}\"]').click();\n"
                    result += f"await markX(page, {r - 1}, {c - 1}); // Place X at ({c} , {r}) {technique.name}\n"

            # coords = [(r + 1, c + 1) for (r, c) in coords]  # convert to 1-based indexing
        result += "  await page.pause();\n"
        result += "  await context.close();\n"
        result += "  await browser.close();\n"
        return result

    def is_solved(self):
        if self.star_count == 0:
            for r in range(self.size):
                if KNOWN_QUEEN not in self.solution[r]:
                    return False
            return True

        # count queens per row
        for r in range(self.size):
            queen_count = sum(1 for c in range(self.size) if self.solution[r][c] == KNOWN_QUEEN)
            if queen_count != self.star_count:
                return False
        return True

    def make_deductions_v2(self):

        for i in range(len(self.techniques)):
            s2 = copy.deepcopy(self)
            s2.simulation_depth = self.simulation_depth
            s2.simulation_mode = False
            progressed = s2.apply_technique(s2.techniques[i])
            if progressed:
                our_unknowns = self.count_unknowns()
                sim_unknowns = s2.count_unknowns()
                unknowns_removed = our_unknowns - sim_unknowns

                r = self.apply_technique(self.techniques[i])
                print("Technique", self.techniques[i].__name__, "removed", unknowns_removed, "unknowns")
                if r != progressed:
                    print("Error: technique progress mismatch")
                    continue
                return progressed
        return False

    def make_deductions(self):
        if self.v2_deductions:
            return self.make_deductions_v2()
        made_progress = self.apply_tier_one_techniques()
        if not self.ntuple_checks_run:
            for i in range(2, self.size // 2):
                # progress = self.find_color_triples() or progress
                made_progress = self.find_ntuples_with_only_n_possibles(i) or made_progress
                made_progress = self.find_color_ntuples(i) or made_progress
            self.ntuple_checks_run = True

        made_progress = self.apply_tier_two_techniques() or made_progress
        made_progress = self.mark_x_for_single_squares() or made_progress
        made_progress = self.find_single_possibilities() or made_progress
        if made_progress and not self.is_solved() and self.attempts < 2:
            return made_progress
        else:
            made_progress = self.test_placing_queen_eliminates_color() or made_progress

            made_progress = self.test_placing_queen_causes_obvious_conflict() or made_progress if not made_progress else made_progress
        made_progress = self.apply_tier_three_techniques()
        if not made_progress and self.attempts >= 2:
            made_progress = self.simulate() or made_progress

        return made_progress

    def apply_technique(self, technique_func):
        try:
            return technique_func()
        except Exception as e:
            if self.simulation_mode:
                print("Simulation mode: ignoring exception in technique", technique_func.__name__)
                return False
            else:
                print(f"Error applying technique {technique_func.__name__}: {e}")
                traceback.print_exc()
                return False

    def apply_tier_one_techniques(self):
        progress = False
        progress = self.mark_x_for_single_squares() or progress
        while progress:
            # precondition: progress is True
            # postcondition: progress is True
            #                AND we have run find_single_possibilities to exhaustion
            # keep doing this until it fails
            tmp_progress = self.find_single_possibilities()
            self.mark_x_for_single_squares()
            if not tmp_progress:
                break

        progress = self.do_find_lines() or progress
        return progress

    def apply_tier_two_techniques(self):
        progress = self.apply_tier_one_techniques()
        if progress:
            return progress
        progress = self.find_ntuples_with_only_n_possibles(2) or progress
        if progress:
            return progress
        progress = self.find_color_ntuples(2) or progress
        if progress:
            return progress
        progress = self.find_single_possibilities() or progress
        progress = self.find_ntuples_with_only_n_possibles(5) or progress
        progress = self.find_ntuples_with_only_n_possibles(4) or progress

        return progress

    def apply_tier_three_techniques(self):
        progress = self.apply_tier_two_techniques()
        if progress:
            return progress
        for i in range(2, min(self.size, 5)):
            # progress = self.find_color_triples() or progress
            progress = self.find_ntuples_with_only_n_possibles(i) or progress
            progress = self.find_color_ntuples(i) or progress
        progress = self.test_placing_queen_eliminates_color() or progress
        progress = self.find_single_possibilities() or progress
        progress = self.test_placing_queen_causes_obvious_conflict() or progress

        if not progress:
            progress = self.simulate() or progress
        return progress

    def mark_x(self, row, column):
        if self.solution[row][column] == UNKNOWN_VALUE:
            self.solution[row][column] = KNOWN_EMPTY

    def find_color_2tuples(self):
        return self.find_color_ntuples(2)

    def find_color_ntuples_iter(self):
        for n in range(2, self.size - 1):
            if self.find_color_ntuples(n):
                return True
        return False


    def find_color_ntuples(self, n):
        # if there are n colors that are limited to n rows, then mark other colors in those n rows as X
        progress = False
        color_to_rows, color_to_cols = self.get_unknown_rows_and_columns_for_colors()
        color_index_combos = list(itertools.combinations(range(len(self.board)), n))
        new_known_empties: List[Tuple[int, int]] = []
        descriptions: List[str] = []
        # s2 = copy.deepcopy(self)
        # s2.simulation_depth = self.simulation_depth + 1
        # s2.simulation_mode = True
        for ndx in range(len(color_index_combos)):
            colors = [chr(ord('A') + color_index_combos[ndx][i]) for i in range(n)]
            # print(f"Combination: {color1}, {color2}, {color3}")
            if all(color in color_to_rows for color in colors):
                rows_sets = [color_to_rows[color] for color in colors]
                union = list(set().union(*rows_sets))
                union.sort()
                if len(union) == n and all(len(row) > 1 for row in rows_sets):
                    for row in union:
                        for col in range(self.size):
                            if self.board[row][col] not in colors and self.solution[row][col] == UNKNOWN_VALUE:
                                self.mark_x(row, col)
                                new_known_empties.append((row, col))
                                descriptions.append(
                                    f"Rows {[u + 1 for u in union]} can only have colors={','.join(colors)}. Eliminating blocked color {self.board[row][col]} in this row group")
                                progress = True

            if all(color in color_to_cols for color in colors):
                cols_sets = [color_to_cols[color] for color in colors]
                union = list(set().union(*cols_sets))
                union.sort()
                if len(union) == n and all(len(s) > 1 for s in cols_sets):
                    for col in union:
                        for row in range(self.size):
                            if self.board[row][col] not in colors and self.solution[row][col] == UNKNOWN_VALUE:
                                self.mark_x(row, col)
                                new_known_empties.append((row, col))
                                descriptions.append(
                                    f"Cols {[u + 1 for u in union]} can only have colors={','.join(colors)}. Eliminating blocked color {self.board[row][col]} in this col group")
                                progress = True

        # print("Made progress using color_pairs") if progress else None
        if progress:
            self.increment_technique_count(f'find_color_{n}tuples')
            self.add_technique(
                HeuristicTechnique(f'find_color_{n}tuples', difficulty=n, known_empties_marked=new_known_empties,
                                   descriptions=descriptions))
        else:
            self.add_noop_technique(f"find_color_{n}tuples")
        return progress

    def find_ntuples_with_only_n_possibles_iter(self):
        for n in range(2, self.size - 1):
            if self.find_ntuples_with_only_n_possibles(n):
                return True
        return False

    def find_ntuples_with_only_2_possibles(self):
        return self.find_ntuples_with_only_n_possibles(2)

    def find_ntuples_with_only_3_possibles(self):
        return self.find_ntuples_with_only_n_possibles(3)

    def find_ntuples_with_only_4_possibles(self):
        return self.find_ntuples_with_only_n_possibles(4)

    def find_ntuples_with_only_5_possibles(self):
        return self.find_ntuples_with_only_n_possibles(5)

    def find_ntuples_with_only_6_possibles(self):
        return self.find_ntuples_with_only_n_possibles(6)

    def find_ntuples_with_only_7_possibles(self):
        return self.find_ntuples_with_only_n_possibles(7)

    def find_ntuples_with_only_8_possibles(self):
        return self.find_ntuples_with_only_n_possibles(8)

    def find_ntuples_with_only_n_possibles(self, n):
        # if n rows or columns have only n colors that are available, then mark those colors as X everywhere else outside those n rows/cols
        progress = False
        new_known_empties: List[Tuple[int, int]] = []
        descriptions: List[str] = []
        index_combos = list(itertools.combinations(range(len(self.board)), n))

        for index_combo in index_combos:
            # for rz in range(self.size):
            possible_colors_sets = [set() for _ in range(n)]
            for idx, row in enumerate(index_combo):
                for col in range(self.size):
                    if self.solution[row][col] == UNKNOWN_VALUE:
                        possible_colors_sets[idx].add(self.board[row][col])
            all_possible_colors = list(set().union(*possible_colors_sets))
            all_possible_colors.sort()

            if len(all_possible_colors) == n and all(len(s) > 0 for s in possible_colors_sets):
                for r in range(self.size):
                    for c in range(self.size):
                        if self.board[r][c] in all_possible_colors and self.solution[r][
                            c] == UNKNOWN_VALUE and r not in index_combo:
                            self.mark_x(r, c)
                            new_known_empties.append((r, c))
                            descriptions.append(
                                f"rows {', '.join(str(i + 1) for i in index_combo)} are limited to {n} possible colors {all_possible_colors}, eliminating {self.board[r][c]} outside of those rows")
                            progress = True
                if progress:
                    self.add_technique(HeuristicTechnique(f'find_{n}tuples_with_only_{n}_possibles', difficulty=n,
                                                          known_empties_marked=new_known_empties,
                                                          descriptions=descriptions, description="Rows"))
                    return progress

        # now for columns
        for index_combo in index_combos:
            # for cz in range(self.size):
            possible_colors_sets = [set() for _ in range(n)]
            for idx, col in enumerate(index_combo):
                for row in range(self.size):
                    if self.solution[row][col] == UNKNOWN_VALUE:
                        possible_colors_sets[idx].add(self.board[row][col])
            all_possible_colors = list(set().union(*possible_colors_sets))
            all_possible_colors.sort()
            if len(all_possible_colors) == n and all(len(s) > 0 for s in possible_colors_sets):
                for r in range(self.size):
                    for c in range(self.size):
                        if self.board[r][c] in all_possible_colors and self.solution[r][
                            c] == UNKNOWN_VALUE and c not in index_combo:
                            self.mark_x(r, c)
                            new_known_empties.append((r, c))
                            descriptions.append(
                                f"cols {', '.join(str(i + 1) for i in index_combo)} are limited to {n} possible colors {all_possible_colors}, eliminating {self.board[r][c]} outside of those cols")
                            progress = True
                if progress:
                    self.add_technique(HeuristicTechnique(f'find_{n}tuples_with_only_{n}_possibles', difficulty=n,
                                                          known_empties_marked=new_known_empties,
                                                          descriptions=descriptions, description="Columns"))
                    return progress

        if progress:
            assert False
        else:
            self.add_noop_technique(f"find_{n}tuples_with_only_{n}_possibles")
        return progress

    def test_placing_queen_eliminates_color(self, print_debug=False):
        progress = False
        new_known_empties: List[Tuple[int, int]] = []
        descriptions: List[str] = []
        s3 = copy.deepcopy(self)
        s3.simulation_depth = self.simulation_depth + 1
        s3.simulation_mode = True

        for r in range(self.size):
            for c in range(self.size):
                if s3.solution[r][c] == UNKNOWN_VALUE:
                    # if not self.can_place_queen()
                    s2 = copy.deepcopy(s3)
                    s2.simulation_depth = s3.simulation_depth + 1
                    s2.simulation_mode = True
                    if s2.can_place_queen(r, c):
                        if print_debug:
                            print("Testing placing queen at", r, c, "of color", s2.board[r][c])

                        queen_color = s2.board[r][c]
                        s2.set_queen_position(r, c)
                        for color in self.colors:
                            if color != queen_color:
                                found_open = False
                                coords = s2.get_color_coords(color)
                                for (rr, cc) in coords:
                                    if s2.solution[rr][cc] != KNOWN_EMPTY:
                                        found_open = True

                                if not found_open:
                                    if print_debug:
                                        print(
                                            f"Placing queen at {r},{c} of color {queen_color} eliminates color {color}")
                                    if s3.solution[r][c] == UNKNOWN_VALUE:
                                        s3.mark_x(r, c)
                                        progress = True
                                        new_known_empties.append((r, c))
                                        descriptions.append(
                                            f"Placing queen at {(c + 1, r + 1)} of color {queen_color} would wipe {color} out, so marking as X")
                                if progress:
                                    break
                    else:
                        if print_debug:
                            print("Skipping testing placing queen at", r, c, "as can't place queen there")

        if progress:
            self.increment_technique_count('placing_queen_eliminates_color')
            self.difficulty += 2
            self.add_technique(HeuristicTechnique('placing_queen_eliminates_color', difficulty=5,
                                                  known_empties_marked=new_known_empties, descriptions=descriptions))
            self.solution = s3.solution
        else:
            self.add_noop_technique('placing_queen_eliminates_color')
        return progress

    def test_placing_queen_causes_obvious_conflict(self, print_debug=False):
        progress = False
        if self.simulation_mode:
            return False
        for r in range(self.size):
            for c in range(self.size):
                if self.solution[r][c] == UNKNOWN_VALUE:
                    # if not self.can_place_queen()
                    s2 = copy.deepcopy(self)
                    s2.simulation_depth = self.simulation_depth + 1
                    s2.simulation_mode = True
                    if s2.can_place_queen(r, c):
                        if print_debug:
                            print("Testing placing queen at", r, c, "of color", s2.board[r][c])

                        queen_color = s2.board[r][c]
                        s2.set_queen_position(r, c)
                        s2.find_single_possibilities()
                        # s2.mark_x_for_single_squares()
                        # s2.simulation_mode = False
                        if s2.is_invalid_state():
                            # s2.print_solution()
                            if print_debug:
                                print(f"Placing queen at {r},{c} of color {queen_color} causes obvious conflict")
                            self.mark_x(r, c)
                            progress = True
                            self.increment_technique_count('placing_queen_causes_obvious_conflict')
                            self.difficulty += 4
                            extra_steps = s2.get_solution_steps(start_step=len(self.techniques_used)+1, extra_padding="\t\t\t\t", step_prefix="(Sub) ")
                            # print("Extra steps:\n", extra_steps)
                            self.add_technique(HeuristicTechnique('placing_queen_causes_obvious_conflict', difficulty=6,
                                                                  known_empties_marked=[(r, c)],
                                                                  description="\n".join(
                                                                      [s2.get_invalid_description(), extra_steps])))
                            return progress
                    else:
                        if print_debug:
                            print("Skipping testing placing queen at", r, c, "as can't place queen there")
                # else:
                # if print_debug:
                # print("Skipping testing placing queen at", r, c, "as already known", self.solution[r][c])

        if progress:
            self.increment_technique_count('placing_queen_causes_obvious_conflict')
            self.difficulty += 4
        else:
            self.add_noop_technique('placing_queen_causes_obvious_conflict')
        return progress

    def assuming_no_queen_causes_conflict(self, print_debug=False):
        progress = False
        if self.simulation_mode:
            return False
        for r in range(self.size):
            for c in range(self.size):
                if self.solution[r][c] == UNKNOWN_VALUE:
                    # if not self.can_place_queen()
                    s2 = copy.deepcopy(self)
                    s2.simulation_depth = self.simulation_depth + 1
                    s2.simulation_mode = True
                    if s2.can_place_queen(r, c):
                        if print_debug:
                            print("Testing assuming X at", r, c, "of color", s2.board[r][c])

                        # queen_color = s2.board[r][c]
                        s2.board[r][c] = KNOWN_EMPTY
                        s2.find_single_possibilities()
                        # s2.simulation_mode = False
                        if s2.is_invalid_state():
                            # s2.print_solution()
                            if print_debug:
                                print(f"Assuming no queen at {r},{c} causes obvious conflict")
                            self.set_queen_position(r, c)
                            progress = True
                            self.increment_technique_count('assuming_no_queen_causes_conflict')
                            self.difficulty += 4
                            # extra_steps = s2.get_solution_steps(start_step=len(self.techniques_used))
                            extra_steps = s2.get_solution_steps(start_step=len(self.techniques_used)+1, extra_padding="\t\t\t\t", step_prefix="(Sub) ")
                            self.add_technique(HeuristicTechnique('assuming_no_queen_causes_conflict', difficulty=8,
                                                                  queens_placed=[(r, c)],
                                                                  description="\n".join(
                                                                      [s2.get_invalid_description(), extra_steps])))
                            return progress

                # else:
                # if print_debug:
                # print("Skipping testing placing queen at", r, c, "as already known", self.solution[r][c])

        if progress:
            self.increment_technique_count('assuming_no_queen_causes_conflict')
            self.difficulty += 4
        else:
            self.add_noop_technique('assuming_no_queen_causes_conflict')
        return progress

    def find_single_possibilities(self):
        progress = False
        mark_known_empty_techniques = list()
        new_known_empties: List[Tuple[int, int]] = []
        descriptions = list()
        mark_empty_colors = set()

        for color in self.colors:
            coords = self.get_color_coords(color)
            vals = [self.solution[r][c] for (r, c) in coords]
            if vals.count(KNOWN_QUEEN) == 1:
                continue
            if vals.count(UNKNOWN_VALUE) == 1:
                for (r, c) in coords:
                    if self.solution[r][c] == UNKNOWN_VALUE:
                        # print("setting queen at ", r, c, "for color", color, "as it's the only position left for that color")
                        # place_queen_techniques.append('only_one_position_for_color')
                        progress = True
                        self.add_technique(
                            HeuristicTechnique(name="find_single_possibilities__only_one_position_for_color",
                                               difficulty=0, queens_placed=[(r, c)],
                                               descriptions=[
                                                   f"Placed queen at {(c + 1, r + 1)} as it's the only position left for color {color}"]))
                        self.set_queen_position(r, c)
                        # break
        # Go row by row and get count of queens,Xs and unknowns per row
        for row in range(self.size):
            row_vals = self.solution[row]
            if row_vals.count(KNOWN_QUEEN) == 0 and row_vals.count(UNKNOWN_VALUE) == 1:
                col = row_vals.index(UNKNOWN_VALUE)
                color = self.board[row][col]
                # print("setting queen at ", row, col, "for color", color, "as it's the only position left in that row")
                progress = True
                self.add_technique(
                    HeuristicTechnique(name="find_single_possibilities__only_one_position_in_row", difficulty=1,
                                       queens_placed=[(row, col)],
                                       descriptions=[
                                           f"Placed queen at {(col + 1, row + 1)} as it's the only open position in row {row + 1} with color {color}"]))
                self.set_queen_position(row, col)
            # if progress:
            #     break

        # Go col by col and get count of queens,Xs and unknowns per col
        for col in range(self.size):
            col_vals = [self.solution[row][col] for row in range(self.size)]
            if col_vals.count(KNOWN_QUEEN) == 0 and col_vals.count(UNKNOWN_VALUE) == 1:
                row_index = col_vals.index(UNKNOWN_VALUE)
                color = self.board[row_index][col]
                # print("setting queen at ", row, col, "for color", color, "as it's the only position left in that row")
                progress = True
                self.add_technique(
                    HeuristicTechnique(name="find_single_possibilities__only_one_position_in_col", difficulty=1,
                                       queens_placed=[(row_index, col)],
                                       descriptions=[
                                           f"Placed queen at {(col + 1, row_index + 1)} as it's the only open position in col {col + 1} with color {color}"]))
                self.set_queen_position(row_index, col)

        s2 = copy.deepcopy(self)
        s2.simulation_depth = self.simulation_depth + 1
        s2.simulation_mode = True
        # if a row has only one color that it can be, then mark that color everywhere else as X
        for row in range(self.size):
            possible_colors = set()
            for col in range(self.size):
                if s2.solution[row][col] == UNKNOWN_VALUE:
                    possible_colors.add(self.board[row][col])
            if len(possible_colors) == 1:
                color = possible_colors.pop()

                for r in range(self.size):
                    for c in range(self.size):
                        if self.board[r][c] == color and s2.solution[r][c] == UNKNOWN_VALUE and r != row:
                            s2.mark_x(r, c)
                            mark_known_empty_techniques.append('row_contains_only_one_color')
                            descriptions.append(f"Row {row + 1} can only contain color {color}")
                            new_known_empties.append((r, c))
                            mark_empty_colors.add(color)
                            progress = True
            # if progress:
            #     break

        # if a column has only one color that it can be, then mark that color everywhere else as X
        for col in range(self.size):
            possible_colors = set()
            for row in range(self.size):
                if s2.solution[row][col] == UNKNOWN_VALUE:
                    possible_colors.add(self.board[row][col])
            if len(possible_colors) == 1:
                color = possible_colors.pop()
                for r in range(self.size):
                    for c in range(self.size):
                        if self.board[r][c] == color and s2.solution[r][c] == UNKNOWN_VALUE and c != col:
                            s2.mark_x(r, c)
                            mark_known_empty_techniques.append('col_contains_only_one_color')
                            descriptions.append(f"Col {col + 1} can only contain color {color}")
                            new_known_empties.append((r, c))
                            mark_empty_colors.add(color)
                            progress = True
            # if progress:
            #     break

        # print("Made progress using single_possibilities") if progress else None
        if progress:
            if len(mark_known_empty_techniques) > 0:
                self.add_technique(HeuristicTechnique(name="find_single_possible", difficulty=2,
                                                      known_empties_marked=new_known_empties, descriptions=descriptions,
                                                      color=mark_empty_colors))
                self.solution = s2.solution
            for i in range(len(mark_known_empty_techniques)):
                tech = mark_known_empty_techniques[i]
                self.increment_technique_count(f"find_single_possibilities__{tech}")

        else:
            self.add_noop_technique('find_single_possibilities')
        return progress

    def mark_x_for_single_squares(self):
        unknown_color_counts = {}
        made_progress = False
        new_place_queens: List[Tuple[int, int]] = []
        new_difficulties = []
        descriptions: List[str] = []
        s2 = copy.deepcopy(self)
        s2.simulation_depth = self.simulation_depth + 1
        s2.simulation_mode = True

        # for row in range(len(self.board)):
        #     if there's only 1 unkno

        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                if self.solution[row][column] == UNKNOWN_VALUE:
                    color = self.board[row][column]
                    if color not in unknown_color_counts:
                        unknown_color_counts[color] = []
                    unknown_color_counts[color].append((row, column))

        for color, positions in unknown_color_counts.items():
            if len(positions) == self.star_count:
                row, col = positions[0]
                if s2.can_place_queen(row, col):
                    s2.set_queen_position(row, col)
                    new_place_queens.append((row, col))
                    descriptions.append(
                        f"Placed queen at {(col + 1, row + 1)} as it's the only position left for color {color}")
                    coords = s2.get_color_coords(color)
                    if len(coords) == 1:
                        # decrease difficulty since this was a gimme
                        if not self.simulation_mode:
                            print("Difficulty decreased by 3 for placing queen at", row, col, "of color", color,
                                  "as it's the only position left for that color")
                        self.difficulty -= 3
                        new_difficulties.append(-3)

                    else:
                        new_difficulties.append(0)
                    # print("Placing queen at", row, col, "of color", color, "as it's the only position left for that color")
                    made_progress = True

        # print("Made progress using single_squares") if made_progress else None
        if made_progress:
            self.increment_technique_count('mark_queen_for_single_squares')
            # for i in range(len(new_place_queens)):
            #     new_queen_coords = new_place_queens[i]
            #     difficulty_change = new_difficulties[i]
            # sum up new_difficulties
            difficulty_change = sum(new_difficulties)
            self.add_technique(HeuristicTechnique(name="mark_queen_for_single_squares", difficulty=difficulty_change,
                                                  queens_placed=new_place_queens,
                                                  descriptions=descriptions))
            self.solution = s2.solution
        else:
            self.add_noop_technique('mark_x_for_single_squares')

        return made_progress

    def find_lines(self):
        progress = self.do_find_lines()
        while progress:
            self.mark_x_for_single_squares()
            if not self.do_find_lines():
                break
        return progress

    def do_find_lines(self):
        progress = False
        # if a color can only go in one row, mark other colors in that row as X
        color_to_rows, color_to_cols = self.get_unknown_rows_and_columns_for_colors()
        new_known_empties: List[Tuple[int, int]] = []
        descriptions = []
        for color, rows in color_to_rows.items():
            if len(rows) == 1:
                row = list(rows)[0]
                for col in range(self.size):
                    if self.board[row][col] != color and self.solution[row][col] == UNKNOWN_VALUE:
                        self.mark_x(row, col)
                        new_known_empties.append((row, col))
                        descriptions.append(f"Row {row + 1} is horizontal line of {color}")
                        progress = True
                # special case, if length of line is 2 mark the squares above and below as X
                column_list = list(color_to_cols[color])
                column_list.sort()
                if len(column_list) == 2 and column_list[0] + 1 == column_list[1]:
                    for col in color_to_cols[color]:
                        if row > 0 and self.solution[row - 1][col] == UNKNOWN_VALUE:
                            self.mark_x(row - 1, col)
                            new_known_empties.append((row - 1, col))
                            descriptions.append(f"Above neighbor of length 2 line of color {color}")
                            progress = True
                        if row < self.size - 1 and self.solution[row + 1][col] == UNKNOWN_VALUE:
                            self.mark_x(row + 1, col)
                            new_known_empties.append((row + 1, col))
                            descriptions.append(f"Below neighbor of length 2 line of color {color}")
                            progress = True

                if len(column_list) == 3 and column_list[0] + 1 == column_list[1] and column_list[1] + 1 == column_list[
                    2]:
                    # in this case we have a solid line, length 3 so mark squares above and below middle as X
                    # print("Debug: marking neighbors for solid line of 3", color_to_rows[color], "cols", column_list)
                    if row > 0 and self.solution[row - 1][column_list[1]] == UNKNOWN_VALUE:
                        self.mark_x(row - 1, column_list[1])
                        new_known_empties.append((row - 1, column_list[1]))
                        descriptions.append(f"Above neighbor of middle of length 3 line of color {color}")
                        progress = True
                    if row < self.size - 1 and self.solution[row + 1][column_list[1]] == UNKNOWN_VALUE:
                        self.mark_x(row + 1, column_list[1])
                        new_known_empties.append((row + 1, column_list[1]))
                        descriptions.append(f"Below neighbor of middle of length 3 line of color {color}")
                        progress = True
            if progress:
                self.increment_technique_count('find_lines')
                self.add_technique(
                    HeuristicTechnique(name="find_lines", difficulty=0.5, known_empties_marked=new_known_empties,
                                       descriptions=descriptions, description="Horizontal line"))
                return progress

        for color, cols in color_to_cols.items():
            if len(cols) == 1:
                col = list(cols)[0]
                for row in range(self.size):
                    if self.board[row][col] != color and self.solution[row][col] == UNKNOWN_VALUE:
                        self.mark_x(row, col)
                        new_known_empties.append((row, col))
                        descriptions.append(f"Column {col + 1} is vertical line of {color}")
                        progress = True
                #    special case, if length of line is 2 mark the squares left and right as X
                # if color == 'H':
                #     print("Debug: color H in single row", color_to_rows[color], list(color_to_rows[color]), list(color_to_rows[color])[0] == list(color_to_rows[color])[1] + 1)
                rows_for_color = list(color_to_rows[color])
                rows_for_color.sort()
                if len(rows_for_color) == 2 and rows_for_color[0] + 1 == rows_for_color[1]:
                    # print("Debug: marking neighbors", color_to_rows[color], "cols", color_to_cols[color])
                    for row in color_to_rows[color]:
                        if col > 0 and self.solution[row][col - 1] == UNKNOWN_VALUE:
                            self.mark_x(row, col - 1)
                            new_known_empties.append((row, col - 1))
                            descriptions.append(f"Left neighbor of length 2 line of color {color}")
                            progress = True
                        if col < self.size - 1 and self.solution[row][col + 1] == UNKNOWN_VALUE:
                            self.mark_x(row, col + 1)
                            new_known_empties.append((row, col + 1))
                            descriptions.append(f"Right neighbor of length 2 line of color {color}")
                            progress = True

                if len(rows_for_color) == 3 and rows_for_color[0] + 1 == rows_for_color[1] and rows_for_color[1] + 1 == \
                        rows_for_color[2]:
                    # in this case we have a solid line, length 3 so mark squares around middle as X
                    # print("Debug: marking neighbors for solid line of 3", color_to_rows[color], "rows", rows_for_color)
                    if col > 0 and self.solution[rows_for_color[1]][col - 1] == UNKNOWN_VALUE:
                        self.mark_x(rows_for_color[1], col - 1)
                        descriptions.append(f"Left neighbor of middle of length 3 line of color {color}")
                        new_known_empties.append((rows_for_color[1], col - 1))
                        progress = True
                    if col < self.size - 1 and self.solution[rows_for_color[1]][col + 1] == UNKNOWN_VALUE:
                        self.mark_x(rows_for_color[1], col + 1)
                        new_known_empties.append((rows_for_color[1], col + 1))
                        descriptions.append(f"Right neighbor of middle of length 3 line of color {color}")
                        progress = True

            if progress:
                self.increment_technique_count('find_lines')
                # for coord in new_known_empties:
                # print("Marking X at", coord, "due to line deduction")
                self.add_technique(
                    HeuristicTechnique(name="find_lines", difficulty=0, known_empties_marked=new_known_empties,
                                       descriptions=descriptions, description="Vertical line"))
                return progress
            else:
                self.add_noop_technique('find_lines')

        assert not progress  # should have gotten out earlier if made progress
        return progress

    def simulate(self):
        # drastic, but effective
        if self.simulation_depth > 3:
            print("Debug: simulation depth exceeded", self.simulation_depth)
            return False
        progress = False
        for row in range(self.size):
            for col in range(self.size):
                if self.solution[row][col] == UNKNOWN_VALUE:
                    s2 = copy.deepcopy(self)
                    s2.simulation_depth = self.simulation_depth + 1
                    s2.simulation_mode = True
                    if s2.can_place_queen(row, col):
                        s2.set_queen_position(row, col)
                        s2.make_deductions()
                        if s2.is_solved():
                            # print("Simulation placing queen at", row, col,
                            #       "led to solution, so placing queen there. Depth", self.simulation_depth + 1)
                            self.add_technique(
                                HeuristicTechnique(name="simulation", difficulty=8, queens_placed=[(row, col)],
                                                   descriptions=["Simulation led to solution with queen here"]))
                            self.set_queen_position(row, col)
                            self.difficulty += 1
                            progress = True
                        if s2.is_invalid_state():
                            # print("Simulation placing queen at", row, col,
                            #       "led to invalid state, so marking X there. Depth", self.simulation_depth + 1)
                            invalid_state_description = s2.get_invalid_description()
                            self.add_technique(
                                HeuristicTechnique(name="simulation", difficulty=10, known_empties_marked=[(row, col)],
                                                   descriptions=[
                                                       "Simulation led to invalid state with queen here, setting this as X"],
                                                   description=invalid_state_description))
                            self.mark_x(row, col)
                            self.difficulty += 2
                            progress = True
        if progress:
            self.increment_technique_count('simulation')
        else:
            self.add_noop_technique('simulation')

        return progress

    def set_queen_position(self, row, col):
        self.solution[row][col] = KNOWN_QUEEN
        size = self.size
        for r in range(size):
            if r != row:
                self.mark_x(r, col)
        for c in range(size):
            if c != col and self.solution[row][c] == UNKNOWN_VALUE:
                self.mark_x(row, c)
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                r, c = row + dr, col + dc
                if 0 <= r < size and 0 <= c < size:
                    self.mark_x(r, c)

        queen_color = self.board[row][col]
        for r in range(size):
            for c in range(size):
                if self.board[r][c] == queen_color and (r != row or c != col):
                    self.mark_x(r, c)

    def can_place_queen(self, row, column):
        if self.solution[row][column] == KNOWN_EMPTY:
            return False
        size = self.size
        coords_for_color = self.get_color_coords(self.board[row][column])
        for other_row, other_col in coords_for_color:
            if self.solution[other_row][other_col] == KNOWN_QUEEN:
                return False

        for r in range(size):
            if self.solution[r][column] == KNOWN_QUEEN:
                return False
        for c in range(size):
            if self.solution[row][c] == KNOWN_QUEEN:
                return False
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                r, c = row + dr, column + dc
                if 0 <= r < size and 0 <= c < size:
                    if self.solution[r][c] == KNOWN_QUEEN:
                        return False

        return True

    def get_unknown_rows_and_columns_for_colors(self):
        color_to_rows = {}
        color_to_columns = {}
        for row in range(self.size):
            for col in range(self.size):
                if self.solution[row][col] == UNKNOWN_VALUE:
                    color = self.board[row][col]

                    if color not in color_to_rows:
                        color_to_rows[color] = set()
                    color_to_rows[color].add(row)
                    if color not in color_to_columns:
                        color_to_columns[color] = set()
                    color_to_columns[color].add(col)
        # print("Color to rows mapping:", color_to_rows)
        return color_to_rows, color_to_columns

    def get_color_coords(self, color):
        coords = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == color:
                    coords.append((r, c))
        return coords

    def get_solution(self):
        if self.is_solved():
            result = [(0, 0)] * self.size
            for row in range(self.size):
                result[row] = (row + 1, self.solution[row].index(KNOWN_QUEEN) + 1)
            return result
        else:
            return None

    def print_solution(self):
        # solution looks like [(1, 3), (2, 14), (3, 6), (4, 13), (5, 11), (6, 9), (7, 16), (8, 8), (9, 5), (10, 17), (11, 12), (12, 15), (13, 7), (14, 10), (15, 1), (16, 4), (17, 2)]
        result = [0] * self.size
        if self.is_solved():
            solution = self.get_solution()
            print("Heuristic Solution:", solution)
        else:
            print("No complete solution found yet.")

    def increment_technique_count(self, technique):
        # if technique not in self.techniques:
        #     self.techniques[technique] = 0
        if self.is_invalid_state() and not self.simulation_mode:
            print("Invalid state detected after applying technique:", technique)
            assert False
        # self.techniques.append(technique)

    def add_technique(self, technique: HeuristicTechnique):

        if self.is_solved():
            print("Warning: adding technique after already solved:", technique)
            traceback.print_stack()
        if self.is_invalid_state() and not self.simulation_mode:
            print("Invalid state detected after applying technique:", technique)
            assert False

        # self.techniques.append(technique.name)
        self.techniques_used.append(technique)

    def is_invalid_state(self):
        for r in range(self.size):
            if KNOWN_QUEEN not in self.solution[r] and all(
                    self.solution[r][c] == KNOWN_EMPTY for c in range(self.size)):
                if not self.simulation_mode:
                    print("Invalid state at row", r, self.solution[r], self.get_technique_names(), self.solution[r])
                return True
        for c in range(self.size):
            if all(self.solution[r][c] == KNOWN_EMPTY for r in range(self.size)):
                if not self.simulation_mode:
                    print("Invalid state at column", c, self.get_technique_names(),
                          list((self.solution[r][c] for r in range(self.size))))
                return True
        for color in self.colors:
            coords = self.get_color_coords(color)
            if all(self.solution[r][c] == KNOWN_EMPTY for (r, c) in coords):
                if not self.simulation_mode:
                    print("Invalid state at color", color, "coords", coords, self.get_technique_names())
                return True
        return False

    def get_invalid_description(self):
        result = ""
        assert self.is_invalid_state()
        for r in range(self.size):
            if KNOWN_QUEEN not in self.solution[r] and all(
                    self.solution[r][c] == KNOWN_EMPTY for c in range(self.size)):
                result += f"All Xs in row {r + 1}. "
        for c in range(self.size):
            if all(self.solution[r][c] == KNOWN_EMPTY for r in range(self.size)):
                result += f"All Xs in column {c + 1}. "

        for color in self.colors:
            coords = self.get_color_coords(color)
            if all(self.solution[r][c] == KNOWN_EMPTY for (r, c) in coords):
                result += f"All Xs in color {color}. \n"
        return result

    def get_technique_names(self):
        return [t.name for t in self.techniques_used]

    def add_noop_technique(self, param):
        self.noop_techniques.append(param)

    def count_unknowns(self):
        count = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.solution[r][c] == UNKNOWN_VALUE:
                    count += 1
        return count
