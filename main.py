import pygame
from classes.GameClass import Game
import os

pygame.init()

Asset = 'Nicest_Assets'
same_val = 700
WINDOW_WIDTH, WINDOW_HEIGHT, WIDTH, HEIGHT = {'Assets': (same_val, same_val, same_val, same_val),
                                              'Nicest_Assets': (800, 800, 400, 400)}[Asset]

OFF_SET = 200 if Asset == 'Nicest_Assets' else 0
off_set_percentage = {'Assets': 0.15714285714285714, 'Nicest_Assets': 1/4}
off_set_percentage = off_set_percentage[Asset]

off_sets = {'left': WINDOW_WIDTH * off_set_percentage, 'right': WINDOW_WIDTH * (1 - off_set_percentage),
            'up': WINDOW_HEIGHT * off_set_percentage, 'down': WINDOW_HEIGHT * (1 - off_set_percentage)}

SQUARE_WIDTH, SQUARE_HEIGHT = (abs(off_sets['left'] - off_sets['right']) / 8,
                               abs(off_sets['up'] - off_sets['down']) / 8)

CIRCLE_RADIUS = SQUARE_WIDTH / 10

DISTANCE_PERCENTAGE = 0.1
SQUARE_OFF_SET = {'vertical': SQUARE_HEIGHT * DISTANCE_PERCENTAGE,
                  'horizontal': SQUARE_WIDTH * DISTANCE_PERCENTAGE}

PIECE_PERCENTAGE = 0.2
PIECE_WIDTH = SQUARE_WIDTH * (1 - PIECE_PERCENTAGE)
PIECE_HEIGHT = SQUARE_HEIGHT * (1 - PIECE_PERCENTAGE)

WIDTH_DISTANCE = off_sets['left'] + SQUARE_OFF_SET['horizontal']
HEIGHT_DISTANCE = off_sets['up'] + SQUARE_OFF_SET['vertical']

# the width_distance and height_distance will be used to draw a nice rectangle showing a piece has been selected
# and if a piece has been moved, etc.

RECTANGLE_WIDTH = SQUARE_WIDTH - SQUARE_OFF_SET['horizontal'] / 2
RECTANGLE_HEIGHT = SQUARE_HEIGHT - SQUARE_OFF_SET['vertical'] / 2

win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Chess multiplayer game')

BACKGROUND = pygame.image.load(f'{Asset}/board_alt.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))

font = pygame.font.Font(None, 50)

IMAGES = {}
for file in os.listdir(f"./Assets/"):
    if file.endswith('.png') and "alt" not in file:
        color, _ = file.split("_")
        piece, _ = file.split("_")[1].split(".")
        file = f"Assets/{file}"
        if str(piece) not in IMAGES:
            IMAGES[str(piece)] = [pygame.transform.scale(pygame.image.load(file), (PIECE_WIDTH, PIECE_HEIGHT))]
            IMAGES[str(piece)] = {color: pygame.transform.scale(pygame.image.load(file),
                                                                (PIECE_WIDTH, PIECE_HEIGHT))}
        else:
            IMAGES[str(piece)][color] = pygame.transform.scale(pygame.image.load(file),
                                                               (PIECE_WIDTH, PIECE_HEIGHT))


def display_menu(window, piece_color):

    images = {'black': [IMAGES['rook']['white'], IMAGES['bishop']['white'],
                        IMAGES['queen']['white'], IMAGES['knight']['white']],
              'white': [IMAGES['rook']['black'], IMAGES['bishop']['black'],
                        IMAGES['queen']['black'], IMAGES['knight']['black']]}

    menu_images = images[piece_color]

    x_off_set = 20 + WIDTH / 2
    x_width = 100

    height = 175
    y_off_set = 200 + HEIGHT / 2

    pygame.draw.rect(window, (100, 100, 100), pygame.Rect(WIDTH / 2, HEIGHT/2 + height, 400, 100))
    for i, img in enumerate(menu_images):
        window.blit(img, (x_off_set + i * x_width, y_off_set))


def choose_piece_of_menu(x, y):
    pieces = {0: 'Rook', 1: 'Bishop', 2: 'Queen', 3: 'Knight'}
    col = None

    y_off_set = HEIGHT / 2 + 175
    if y_off_set <= y <= y_off_set + 100:
        if WIDTH / 2 <= x <= WIDTH / 2 + WIDTH:
            x -= 200
            if 0 <= x <= 100:
                col = 0
            elif 100 <= x <= 200:
                col = 1
            elif 200 <= x <= 300:
                col = 2
            elif 300 <= x <= 400:
                col = 3

            return pieces[col]


def get_center_square(row, col):
    x, y = normalize_position((row, col))
    center = (x + SQUARE_WIDTH / 2, y + SQUARE_HEIGHT / 2)
    return center


def draw_eaten_pieces(eaten_pieces, window):

    # top left, top right, bottom left, bottom right
    coordinates = [(200, 190), (600, 190), (200, 610), (610, 610)]
    width = 100
    row_width = 40
    col_width = 30
    col_off_set = 5

    # the white pieces will be drawn on the black's part of the chess board and vice versa
    pieces_coordinates = {'white': {'bottom left': coordinates[0], 'bottom right': coordinates[1],
                                    'top left': (coordinates[0][0], coordinates[0][1] - width),
                                    'top right': (coordinates[1][0], coordinates[1][1] - width)},

                          'black': {'top left': coordinates[2], 'top right': coordinates[3],
                                    'bottom left': (coordinates[2][0], coordinates[2][1] + width),
                                    'bottom right': (coordinates[3][0], coordinates[3][1] + width)}}

    pieces_positions = {'white': {'Rook': [0, 0.5, 0], 'Knight': [0, 2.5, 2], 'Bishop': [0, 4.5, 4],
                                  'Queen': [0, 6], 'King': [0, 7], 'Pawn': [1, 7, 6, 5, 4, 3, 2, 1, 0]},

                        'black': {'Rook': [0, 0.5, 0], 'Knight': [0, 2.5, 2], 'Bishop': [0, 4.5, 4],
                                  'Queen': [0, 6], 'King': [0, 7], 'Pawn': [1, 7, 6, 5, 4, 3, 2, 1, 0]}}

    pieces_information = {'white': {}, 'black': {}}
    pieces_colors = {'white': {}, 'black': {}}

    if eaten_pieces:
        for piece in eaten_pieces:
            color = piece.color
            information = pieces_information[color]
            type_piece, _ = str(piece).split("(")
            positions = pieces_positions[color][type_piece]
            pieces_colors[color][type_piece] = {piece.image}
            if type_piece not in information and type_piece not in ('Pawn', 'King', 'Queen'):
                information[type_piece] = [(positions[0], positions[-1])]
            elif type_piece not in information and type_piece == 'Queen':
                information[type_piece] = positions
            elif type_piece not in information and type_piece == 'King':
                information[type_piece] = positions
            elif type_piece not in information and type_piece == 'Pawn':
                information[type_piece] = [(positions[0], positions[-1])]
                positions.pop()
            else:
                if len(positions) > 2:
                    information[type_piece].append((positions[0], positions[-1]))
                    positions.pop()
                if len(positions) > 1:
                    information[type_piece].append((positions[0], positions[-1]))

            for key in information.keys():
                image, = pieces_colors[color][key]
                for pos in information[key]:
                    (row, col) = (pos if type(pos) is not int else information[key]
                                  if len(information[key]) == 2 else (None, None))
                    if row is None:
                        continue
                    top_left_corner = (pieces_coordinates[color]['top left'][0] + col * col_width + col_off_set,
                                       pieces_coordinates[color]['top left'][1] + row * row_width)
                    window.blit(image, top_left_corner)


def draw(window, background, board, menu_info, click_info=None,
         valid_moves=None, pieces_eaten=None, show_valid_moves=True, check_mate_information=None):
    from classes.BoardClass import Node

    win.fill((100, 100, 100))
    window.blit(background, (OFF_SET, OFF_SET))

    if menu_info:
        menu_color, promotion = menu_info
    else:
        promotion = False

    for row in board.grid:
        for piece in row:
            piece.draw(window)

    if click_info is None:
        pass
    else:
        x, y, row, col = click_info
        if type(board.get_piece(row, col)) is Node:
            pass
        else:
            if valid_moves and show_valid_moves:
                for move in valid_moves:
                    r, c = move
                    center = get_center_square(r, c)
                    pygame.draw.circle(window, 'red', center, CIRCLE_RADIUS)

            pygame.draw.rect(window, 'red', pygame.Rect(x, y, RECTANGLE_WIDTH, RECTANGLE_HEIGHT), 4)
    draw_eaten_pieces(pieces_eaten, win)
    if promotion:
        display_menu(window, menu_color)
    if check_mate_information:
        text = font.render(f"{check_mate_information} player wins!", True, 'green', 'blue')
        another_game = font.render('If you want to play again press the SPACE key.', True, 'black', 'red')
        window.blit(text, (250, 100))
        window.blit(another_game, (10, 400))

    pygame.display.update()


def get_row_col(mouse_position):
    """
    :param mouse_position: tuple
    :return: tuple

    We want to return the corresponding row and col of the chessboard. First we normalize the mouse_position
    by resetting the values using the offsets.
    """
    x, y = mouse_position
    x -= off_sets['left']
    y -= off_sets['up']

    row = int(y / SQUARE_HEIGHT)
    col = int(x / SQUARE_WIDTH)
    return row, col


def normalize_position(board_position):
    row, col = board_position

    x = col * SQUARE_WIDTH + off_sets['left']
    y = row * SQUARE_HEIGHT + off_sets['up']

    x += SQUARE_OFF_SET['horizontal'] / 3
    y += SQUARE_OFF_SET['vertical'] / 3

    return x, y


def initial_state():
    return True, None, [], [], None, False, None


def main():

    from classes.BoardClass import Board

    (run, click_info, valid_moves, pieces_eaten, menu_info,
     select_piece_from_menu, check_mate_information) = initial_state()

    board = Board()
    game = Game(board)

    print("If you want to see the possible moves of the different pieces write True."
          "If you do not want to see them write False")
    show_valid_moves_string = input()

    if show_valid_moves_string == 'True':
        show_valid_moves = True
    elif show_valid_moves_string == 'False':
        show_valid_moves = False

    promotion = None

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and not promotion and not select_piece_from_menu:
                x, y = pygame.mouse.get_pos()
                if off_sets['left'] <= x <= off_sets['right'] and off_sets['up'] <= y <= off_sets['down']:
                    game.track_kings()
                    if game.piece is None:
                        row, col = get_row_col((x, y))
                        pos = normalize_position((row, col))
                        click_info, valid_moves = game.select_piece(row, col, pos[0], pos[1])
                    else:
                        new_row, new_col = get_row_col((x, y))
                        old_piece = game.move((new_row, new_col))
                        if type(old_piece) is tuple or old_piece is None:
                            x, y = normalize_position((new_row, new_col))
                            click_info, valid_moves = game.select_piece(new_row, new_col, x, y)
                        else:
                            pieces_eaten.append(old_piece)

                promotion = game.any_promotion()
                check_mate_information = game.check_mate()
                if promotion:
                    menu_info = game.color, promotion[0]
                    select_piece_from_menu = True

            elif event.type == pygame.MOUSEBUTTONDOWN and promotion and select_piece_from_menu:
                x, y = pygame.mouse.get_pos()
                if choose_piece_of_menu(x, y):
                    menu_piece = choose_piece_of_menu(x, y)
                    game.promote(menu_piece, promotion[-1])
                    menu_info = None
                select_piece_from_menu = False
                promotion = False

            if event.type == pygame.KEYDOWN and check_mate_information:
                key = pygame.KEYDOWN
                another_game = game.another_game(key)
                if not another_game:
                    run = False
                    break
                else:
                    (run, click_info, valid_moves, pieces_eaten, menu_info,
                     select_piece_from_menu, check_mate_information) = initial_state()
                    board = Board()
                    game = Game(board)

        draw(win, BACKGROUND, game.board, menu_info,
             click_info, valid_moves, pieces_eaten,
             show_valid_moves, check_mate_information)
    quit()


if __name__ == "__main__":
    main()
