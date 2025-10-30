# import queens_board_draw as ImgUtil


from queens_board_draw import ImgUtil

board = [
    ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'],
    ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'],
    ['A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'C', 'D', 'D', 'D', 'A', 'A'],
    ['A', 'A', 'E', 'E', 'E', 'A', 'B', 'F', 'B', 'C', 'C', 'D', 'D', 'A', 'A'],
    ['A', 'A', 'E', 'F', 'E', 'A', 'B', 'F', 'B', 'B', 'C', 'F', 'D', 'A', 'A'],
    ['A', 'A', 'E', 'F', 'E', 'E', 'B', 'F', 'B', 'C', 'C', 'F', 'G', 'A', 'A'],
    ['A', 'A', 'E', 'F', 'F', 'E', 'E', 'F', 'B', 'C', 'F', 'F', 'G', 'A', 'A'],
    ['A', 'A', 'E', 'E', 'F', 'F', 'E', 'F', 'B', 'F', 'F', 'G', 'G', 'A', 'A'],
    ['A', 'A', 'E', 'E', 'H', 'F', 'F', 'F', 'F', 'F', 'I', 'I', 'G', 'A', 'A'],
    ['A', 'A', 'E', 'E', 'H', 'H', 'F', 'F', 'F', 'I', 'I', 'I', 'G', 'A', 'A'],
    ['A', 'A', 'E', 'E', 'H', 'H', 'H', 'F', 'I', 'I', 'I', 'I', 'G', 'A', 'A'],
    ['A', 'A', 'J', 'E', 'E', 'E', 'E', 'F', 'I', 'I', 'I', 'I', 'K', 'A', 'A'],
    ['A', 'A', 'J', 'J', 'J', 'J', 'E', 'F', 'I', 'I', 'I', 'K', 'K', 'A', 'A'],
    ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'],
    ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A'],
]
if __name__ == '__main__':
    ImgUtil.draw_board(board, 'Initial_Board')
    # solve_queens('board.png')
    # solve_queens('Test_Boards/LinkedIn_Presolved_Test.png')
