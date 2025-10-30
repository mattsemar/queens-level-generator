import subprocess
import sys

from board_util import normalize_sections


class BoardParser:
    @classmethod
    def parse_lines(cls, lines):
        local_board = []
        uniq_vals = set()
        if len(lines) == 1:
            print("Treating this as a JSON blob")
            import json
            try:
                data = json.loads(lines[0])
                lines = data
                print("Parsed JSON data with", len(lines), "lines")
                return lines

            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                lines = [lines[0]]

        val_counts = { }
        for line in lines:
            # make sure line has single letter entries separated by spaces
            # print("Parsing line:", line.strip())
            line = line.strip()
            if not line or 'Board:' in line:
                continue
            row = line.strip().replace("#", "").replace('[', '').replace(']', '').replace(',', '').replace('\'', '').replace('"', '').split()

            skip_line = False
            for i in range(len(row)):
                # print(f"Row {len(board)} Col {i}: {row[i]}")
                val = row[i].strip().replace("#", "").replace('[', '').replace(']', '').replace(',', '').replace('\'', '').replace('"', '')
                if len(val) != 1:
                    skip_line = True
                    # print(f"Skipping invalid entry in row {len(local_board)} col {i}: {val} {row[i]}")
                    break
                else:
                    row[i] = val
                    uniq_vals.add(val) if val >= 'A' or val <= 'Z' else print("Skipping invalid value:", val)
                    val_counts[val] = val_counts.get(val, 0) + 1
                    # print(f"Row {len(local_board)} Col {i}: {val}")
            if skip_line:
                continue
            local_board.append(row)

        if len(local_board[0]) < len(local_board) < len(local_board[0]) * 1.5:
            # delete extra rows to make it square
            print("Warning: More rows than columns, trimming to square")
            local_board = local_board[:len(local_board[0])]
        print("Unique values found in parsed board:", uniq_vals, "val counts", val_counts, "height:", len(local_board), "width:", len(local_board[0]) if local_board else 0)

        # return normalize_sections( local_board)
        return local_board




# read in a format like this
# A A A B B B B
# A A A B C D D
# E F F F C G D
# E E G F C G D
# E E G F C G G
# E G G F F F G
# E G G G G F F
    # or like
    # Board:
    #     [A, A, A, A, A, A, B, B],
    #     [A, C, C, C, C, C, C, D],
    #     [A, C, C, C, C, C, C, D],
    #     [A, E, E, E, F, F, F, D],
    #     [A, E, E, G, F, H, F, D],
    #     [A, E, E, F, F, H, H, H],
    #     [E, E, E, F, F, H, H, H],
    #     [E, E, E, F, H, H, H, H],
if __name__ == '__main__':
    filename = "queens_board.txt"
    if len(sys.argv) < 2:
        print("Getting lines from paste input")
        result = subprocess.run("pbpaste > queens_board.txt", shell=True)
    else:
        filename = sys.argv[1]
    board_lines = []

    with open(filename, 'r') as file:
        for line in file:
            board_lines.append(line)

    board = BoardParser.parse_lines(board_lines)

    print("board = [")
    for row in board:
        print(f"    {row},")
    print("]")
    uniqs = set()
    for row in board:
        for col in row:
            uniqs.add(col)
    print("Unique colors:", uniqs, "Count:", len(uniqs))
