import argparse
import os

from HeuristicSolver import HeuristicSolver
from queens_board_draw import ImgUtil
from queens_board_parse import BoardParser
from solver import MySolver

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read levels from files in a directory and rank their difficulties.")
    parser.add_argument("directory", type=str, help="Directory containing level files")
    args = parser.parse_args()
    listdir = os.listdir(args.directory)
    print("Generating difficulties...", listdir)
    most_difficult_difficulty = -1
    most_difficult_board = None
    difficulties = []
    for filename in listdir:
        if filename.endswith(".ts") and not filename.startswith("levelSample.ts") and (filename.endswith("level333.ts") or filename.endswith("level273.ts")):
            # if filename.endswith("level210.ts"):
            filepath = os.path.join(args.directory, filename)
            print("Processing file:", filepath)
            inf = open(filepath, 'r')
            lines = inf.readlines()
            # filter out lines before the first "[" and after the last "]", keep
            lines = lines[next((i for i, line in enumerate(lines) if "[" in line), 0):
                          (len(lines) - next((i for i, line in enumerate(reversed(lines)) if "]" in line), 0))]
            # only lines that have "["
            lines = [ line.strip().replace("':", "").replace("colorRegions", "") for line in lines]
            # remove everything but the letters A-Z
            lines = [ line.replace('"', '').replace(",", " ") for line in lines if any(c.isalpha() for c in line)]
            # for line in lines:
            #     print("Line:", line)

            if len(lines) > 18:
                # group into sqrt(n) chunks
                chunk_size = int(len(lines) ** 0.5)
                lines = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
                # join each chunk into a single string
                lines = ["".join(chunk) for chunk in lines]


            print("Processing file:", lines)
            board = BoardParser.parse_lines(lines)
            # if len(board) != 7:
            #     continue
            print("Link:", ImgUtil.generate_request_url(board))
            solution_count, stats, solution, has_one_color, _ = MySolver.count_solutions(board)
            if solution_count == 1:
                solver  = HeuristicSolver(board, v2_deductions=True)
                solver.solve()
                if solver.is_solved():
                    difficulty = solver.difficulty
                    print(f"Board {filename} solved with difficulty {difficulty}")
                    difficulties.append({'file': filename, 'difficulty': difficulty})
                    if difficulty > most_difficult_difficulty:
                        most_difficult_difficulty = difficulty
                        most_difficult_board = filepath
                print(ImgUtil.generate_request_url(board))
            else:
                print(f"Board {filename} has {solution_count} solutions, skipping difficulty rating.")
    print("Most difficult board difficulty:", most_difficult_difficulty, "board:", most_difficult_board)
    difficulties.sort(key=lambda d: d['difficulty'])
    print("All difficulties:")
    for difficulty in difficulties:

        print(difficulty)











