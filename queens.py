import copy
import select
import subprocess

from z3 import *  # type: ignore

from HeuristicSolver import HeuristicSolver
from board_util import normalize_sections
from queens_board_draw import ImgUtil
from queens_board_parse import BoardParser
from queens_generator import generate
from sb_g import generate_star_battle
from solver import MySolver
import argparse


def has_stdin_input():
    """
    Checks if there is input available on stdin without blocking.
    Returns True if input is available, False otherwise.
    """
    # select.select takes three lists: rlist (read), wlist (write), xlist (exceptional)
    # The timeout parameter (0 in this case) makes it non-blocking.
    # sys.stdin is the file object for standard input.
    return select.select([sys.stdin], [], [], 0)[0]


default_board = [
    ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'E', 'E', 'E'],
    ['C', 'C', 'A', 'A', 'D', 'B', 'B', 'B', 'B', 'B', 'B', 'E', 'E', 'E', 'E'],
    ['C', 'D', 'D', 'D', 'D', 'D', 'B', 'B', 'B', 'B', 'B', 'E', 'E', 'E', 'E'],
    ['C', 'F', 'D', 'D', 'D', 'D', 'B', 'B', 'B', 'B', 'K', 'I', 'E', 'E', 'E'],
    ['C', 'F', 'D', 'D', 'D', 'D', 'B', 'B', 'B', 'K', 'K', 'I', 'I', 'E', 'E'],
    ['F', 'F', 'G', 'D', 'D', 'B', 'B', 'B', 'B', 'K', 'K', 'K', 'I', 'E', 'E'],
    ['G', 'G', 'G', 'H', 'J', 'J', 'K', 'K', 'K', 'K', 'I', 'K', 'I', 'I', 'E'],
    ['G', 'G', 'H', 'H', 'J', 'J', 'K', 'K', 'K', 'K', 'I', 'I', 'I', 'E', 'E'],
    ['G', 'G', 'G', 'H', 'J', 'J', 'J', 'K', 'K', 'K', 'I', 'I', 'I', 'I', 'I'],
    ['J', 'J', 'J', 'J', 'J', 'J', 'K', 'K', 'K', 'K', 'O', 'I', 'L', 'I', 'I'],
    ['J', 'N', 'N', 'J', 'J', 'M', 'K', 'K', 'K', 'O', 'O', 'L', 'L', 'L', 'L'],
    ['J', 'N', 'J', 'J', 'J', 'M', 'K', 'K', 'O', 'O', 'O', 'L', 'L', 'L', 'L'],
    ['J', 'N', 'N', 'N', 'M', 'M', 'N', 'O', 'O', 'O', 'O', 'O', 'L', 'L', 'L'],
    ['J', 'J', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'O', 'L', 'L', 'L', 'L'],
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'L', 'L', 'L'],
]

parser = argparse.ArgumentParser(description="Generate or solve Queens board problems.")
subparsers = parser.add_subparsers(dest='command', required=True)

generate_parser = subparsers.add_parser(
    'generate', help='Generate a board')
generate_parser.add_argument(
    '--size', type=int, help='The size of the board', required=True)
generate_parser.add_argument('--template', action='store_true',  default=False, help='Use template for generating board')
generate_parser.add_argument('--max', type=int, help='The maximum number of solutions', default=500)
generate_parser.add_argument("--star-count",  help="Max solutions to check", type=int, default=1)



solve_parser = subparsers.add_parser(
    'solve', help='Solve an existing board')
solve_parser.add_argument(
    '--file', type=str, help='The file containing the board to solve')

draw_parser = subparsers.add_parser('draw', help='Draw the board to an image file')
draw_parser.add_argument('--file', type=str, help='The file to save the board image to', required=False)

solve_parser.add_argument("--draw", nargs=1, type=str, help="Draw board image to file", default=None)
solve_parser.add_argument("--print", type=bool, help="Print out text representation of the board", default=True)
solve_parser.add_argument("--show-solutions",  help="Print all solutions", action='store_true', default=False)
solve_parser.add_argument("--show-steps",  help="Print human readable steps for solving", action='store_true', default=False)
solve_parser.add_argument("--max-solutions",  help="Max solutions to check", type=int, default=100)
solve_parser.add_argument("--star-count",  help="Number of stars for SB", type=int, default=1)
# g.add_argument("--template", type=bool, help="Generate board given template", default=False)

args = parser.parse_args()
# if generate_parser.__class__ == argparse.ArgumentParser:
#     args.command = 'generate'
# elif solve_parser.__class__ == argparse.ArgumentParser:
#     args.command = 'solve'
# else:
#     args.command = 'default'

print(args)

if args.command == 'solve' or args.command == 'draw':
    if args.file:
        f = args.file
        if f == "paste":
            print("Getting lines from paste input")
            result = subprocess.run("pbpaste > queens_board.txt", shell=True)
            f = "queens_board.txt"
        inf = open(f, 'r')
        board_lines = inf.readlines()
        board = BoardParser.parse_lines(board_lines)
        print("Board loaded from file:", args.file)
    elif has_stdin_input():
        print("Loading board from stdin...")
        board_lines = sys.stdin.readlines(-1)  # Read all lines from stdin if not provided a file
        board = BoardParser.parse_lines(board_lines)
    else:
        board = default_board
        if args.command == 'solve':
            print("No input file provided, using default board.")

    if args.command == 'solve':
        boards = []
        if len(board) > len(board[0]) * 2:
            # split board into N boards each of height = columns
            print("Warning: Board has many more rows than columns, may be invalid.", len(board), "rows vs", len(board[0]), "columns")
            cols = len(board[0])
            print(f"Splitting into {len(board) // cols} boards for solving")

            for i in range(1, len(board) // cols):
                boards.append(board[cols * i: cols * (i + 1)])
                ImgUtil.print_board(boards[0])


        else:
            boards.append(board)

        highest_difficulty = 0
        highest_difficulty_index = 0
        for ndx in range(len(boards)):
            board = boards[ndx]
            print("Solving board:")
            nboard = normalize_sections(board)
            print("Normalized board:")
            ImgUtil.print_board(nboard)
            ImgUtil.generate_request_url(nboard)

            print("board = [")
            for row in board:
                print(f"    {row},")
            print("]")

            solutions, stats, sln, _ = MySolver.count_solutions(board, count_all=False,
                                                                print_solutions=args.show_solutions,
                                                                max_solutions=args.max_solutions,
                                                                star_count=args.star_count)
            print("Solutions", solutions, "Decisions", stats.get_key_value('decisions') if stats else 0, "Conflicts",
                  stats.get_key_value('conflicts') if stats else 0)
            if sln is not None:
                print("Solution:", sln)
                # solved_board = normalize_sections(board.copy())
                og_board = copy.deepcopy(board)
                solved_board = board.copy()
                for l in sln:
                    row, col = l
                    solved_board[row - 1][col - 1] = solved_board[row - 1][col - 1] + '_Q'
                print("Solved board:")
                if args.print:
                    ImgUtil.print_board(solved_board, normalize=False)
                if args.draw:
                    ImgUtil.draw_board(solved_board, args.draw)
                heuristic_solver = HeuristicSolver( og_board, v2_deductions=False)
                heuristic_solver.solve()
                if heuristic_solver.is_solved():
                    print("Heuristic solved")
                    heuristic_solver.print_solution()
                    heuristic_solution = heuristic_solver.get_solution()
                    if heuristic_solver.difficulty > highest_difficulty and len(boards) > 1:
                        highest_difficulty = heuristic_solver.difficulty
                        highest_difficulty_index = ndx
                        print("Highest difficulty:", highest_difficulty, "index", highest_difficulty_index)

                    if args.show_steps:
                        print("Heuristic solution:", heuristic_solver.get_solution_steps())

                else:
                    print("Heuristic failed to solve, reported difficulty", heuristic_solver.difficulty)

        if len(boards) > 1:
            print("Highest difficulty was", highest_difficulty, "for board index", highest_difficulty_index)
            ImgUtil.generate_request_url(boards[highest_difficulty_index])


    else:
        print("Drawing board to image file:", args.file)
        ImgUtil.draw_board(board, "test_board", draw_coords=False ,  normalize=False, )

if args.command == 'generate':
    if args.size is not None and args.size > 5 and args.star_count == 1:
        generate(size=args.size, draw=True, use_vanity=args.template, max_boards=args.max)
    elif args.size is not None and args.star_count > 1:
        generate_star_battle(size=args.size, star_count=args.star_count, max_boards=args.max)
    else:
        print(parser.print_help())
