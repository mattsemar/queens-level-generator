def hash_board(board):
    # Generate a hash for the board configuration
    board_str = ''.join(''.join(row) for row in board)
    # print(board_str, "\n")
    return hash(board_str)

def normalize_sections(board):
    # make sure A is top level and b is used next
    from collections import defaultdict
    section_map = {}
    next_section = 'A'
    for row in board:
        for cell in row:
            if cell not in section_map:
                section_map[cell] = next_section
                next_section = chr(ord(next_section) + 1)

    normalized_board = [[section_map[cell] for cell in row] for row in board]
    return normalized_board

def get_region_coords(board):
    result = {}
    for row in range(len(board)):
        for col in range(len(board[row])):
            color = board[row][col]
            if color not in result:
                result[color] = []

            result[color].append((row, col))
    # print("Color to rows mapping:", color_to_rows)
    return result

def get_single_cell_regions(board):
    region_coords = get_region_coords(board)
    single_cell_regions = {color: coords for color, coords in region_coords.items() if len(coords) == 1}
    return single_cell_regions

def has_disconnected_colors(board):
    from collections import deque

    def bfs(start, color):
        queue = deque([start])
        visited = {start}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            x, y = queue.popleft()
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]) and (nx, ny) not in visited and board[nx][ny] == color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return visited

    region_coords = get_region_coords(board)

    for color, coords in region_coords.items():
        if len(coords) <= 1:
            continue

        visited = bfs(coords[0], color)
        if len(visited) != len(coords):
            return True

    return False