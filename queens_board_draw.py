# regionColors: {
#     A: lightWisteria,
#     B: chardonnay,
#     C: anakiwa,
#     D: celadon,
#     E: altoMain,
#     F: bittersweet,
#     G: saharaSand,
#     H: nomad,
#     I: lightOrchid,
#     J: halfBaked,
#     K: turquoiseBlue,
#     L: atomicTangerine,
#     M: lightGreen,
#     N: emerald,
#     O: periwinkle,
# },
from board_util import normalize_sections

color_names = {
    "A": "lightWisteria",
    "B": "chardonnay",
    "C": "anakiwa",
    "D": "celadon",
    "E": "altoMain",
    "F": "bittersweet",
    "G": "saharaSand",
    "H": "nomad",
    "I": "lightOrchid",
    "J": "halfBaked",
    "K": "turquoiseBlue",
    "L": "atomicTangerine",
    "M": "lightGreen",
    "N": "emerald",
    "O": "periwinkle",
    "P": "coldPurple",
    "Q": "macNCheese",
    "R": "lavenderRose",
}

color_hues = {
    "alto": "#D9D9D9",
    "altoMain": "#DFDFDF",
    "anakiwa": "#96BEFF",
    "bittersweet": "#FF7B60",
    "canCan": "#D895B2",
    "carnation": "#F96C51",
    "celadon": "#B3DFA0",
    "chardonnay": "#FFC992",
    "coldPurple": "#AF96DC",
    "emerald": "#5BBA6F",
    "feijoa": "#A6D995",
    "halfBaked": "#95CBCF",
    "lavenderRose": "#FE93F1",
    "lightGreen": "#91F5AD",
    "lightOrchid": "#DFA0BF",
    "lightWisteria": "#BBA3E2",
    "macNCheese": "#FBBF81",
    "malibu": "#85B5FC",
    "manz": "#DCF079",
    "nomad": "#B9B29E",
    "periwinkle": "#C9C9EE",
    "saharaSand": "#E6F388",
    "tallow": "#ADA68E",
    "turquoiseBlue": "#55EBE2",
    "atomicTangerine": "#FAA889",
    "black": "#FFFFFF"
}

color_hue_names = {
      "A": "#5E4FA2",
      "B": "#E6F598",
      "C": "#3287BD",
      "D": "#ACDDA5",
      "E": "#6C7A89",
      "F": "#D53E4F",
      "G": "#E6F598",
      "H": "#8E8875",
      "I": "#F56D43",
      "J": "#8E6E8E",
      "K": "#467A7D",
      "L": "#FAA889",
      "M": "#91F5AD",
      "N": "#5BBA6F",
      "O": "#C9C9EE",
      "P": "#E6F388",
      "Q": "#000000",
      "R": "#FFFFFF",
  }

# colors = {
# "A": tuple( color_hues["lightWisteria"].replace("#", "")[i:i+2] for i in (0, 2, 4) ),
# }


class ImgUtil:
    @classmethod
    def draw_board(cls, board_orig, param, normalize=True, draw_coords=False):
        from PIL import Image, ImageDraw, ImageFont
        import os
        import matplotlib.pyplot as plt
        import numpy as np
        board = normalize_sections(board_orig) if normalize else board_orig

        n = len(board)
        m = len(board[0]) if n > 0 else 0
        cell_size = 75
        img_width = m * cell_size
        img_height = n * cell_size
        img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(img)
        queen_image = Image.open("queen.png").convert("RGBA")

        for i in range(n):
            for j in range(m):

                cell = board[i][j]
                cell_color_key = cell[0] if isinstance(cell, str) and len(cell) > 0 else 'N'
                # fill_color = color_hues[
                #     color_names[cell_color_key]] if cell_color_key in color_names.keys() else "white"
                fill_color = color_hue_names[cell_color_key] if cell_color_key in color_names.keys() else "white"
                if fill_color == "white":
                    print(f"Warning: Color for cell '{cell}' not found in color_hues. Using white.")
                draw.rectangle([j * cell_size, i * cell_size, (j + 1) * cell_size, (i + 1) * cell_size],
                               fill=fill_color, outline="black", width=2)
                # label = labels[i * m + j] if i * m + j < len(labels) else '?'
                # label = cell_color

                if len(cell) > 1 and cell[-1] == 'Q':
                    img.paste(queen_image, (j * cell_size + 5, i * cell_size + 5), mask=queen_image)
                elif len(cell) > 1 and cell[-1] == 'X':
                    draw.text((j * cell_size + cell_size // 3, i * cell_size + cell_size // 3), "X", fill="red")
                elif draw_coords:
                    draw.text((j * cell_size + cell_size // 3, i * cell_size + cell_size // 3), f"({i},{j})", fill="black")
        if not os.path.exists("output"):
            os.makedirs("output")
        filename = f"output/board_{param}.png"
        img.save(filename)
        print(f"Board image saved as {filename}")
        plt.imshow(np.array(img))

    @classmethod
    def print_board(cls, board, normalize=True):
        board = normalize_sections(board) if normalize  else board
        for row in board:
            print("\t".join(row))
        print("\n")

    @classmethod
    def generate_request_url(cls, board):
        sections = normalize_sections(board)
        path_param = "".join(["".join(c) for c in sections])
        print( f"https://queens.semar.dev/random-level/{path_param}")

    @classmethod
    def load_new_image(cls, filepath):
        from PIL import Image

        try:
            img = Image.open(filepath)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")

    @classmethod
    def get_board_matrix(cls, img):
        import numpy as np

        img = img.convert("RGB")
        width, height = img.size
        pixels = np.array(img)

        # Assuming the image is a square grid
        size = int(np.sqrt((width * height) / 3))
        board = [['' for _ in range(size)] for _ in range(size)]
        cell_width = width // size
        cell_height = height // size
        for i in range(size):
            for j in range(size):
                cell = pixels[i * cell_height:(i + 1) * cell_height, j * cell_width:(j + 1) * cell_width]
                avg_color = tuple(np.mean(cell.reshape(-1, 3), axis=0).astype(int))
                board[i][j] = str(avg_color)
        return board
