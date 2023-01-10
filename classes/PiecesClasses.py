from main import (WIDTH_DISTANCE, HEIGHT_DISTANCE,
                  SQUARE_HEIGHT, SQUARE_WIDTH, IMAGES)


class Piece:

    IMAGES = IMAGES
    COL_OFF_SET = WIDTH_DISTANCE
    ROW_OFF_SET = HEIGHT_DISTANCE

    def __init__(self, color, row, col):
        """
        :param color: str or int
        :param row: int
        :param col: int

        Besides that: we want to resize the images.
        """
        self.color = color
        self.row = row
        self.col = col
        self.horizontal_distance = self.col * SQUARE_WIDTH
        self.vertical_distance = self.row * SQUARE_HEIGHT

        self.image = None

    def draw(self, win):
        win.blit(self.image, (self.COL_OFF_SET + self.horizontal_distance,
                              self.ROW_OFF_SET + self.vertical_distance))

    def recalculate_distance(self, new_position):
        new_row, new_col = new_position
        self.horizontal_distance = new_col * SQUARE_WIDTH
        self.vertical_distance = new_row * SQUARE_HEIGHT


class Pawn(Piece):

    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.first_move = True
        self.index = -1 if self.color == 'white' else 1

        self.image = self.IMAGES['pawn'][self.color]

    def valid_move(self, bo):

        valid_moves = []
        if self.first_move:
            possible_moves = ((self.row + 2 * self.index, self.col), (self.row + self.index, self.col),
                              (self.row + self.index, self.col - 1), (self.row + self.index, self.col + 1))

        else:
            # the possibles moves are checked by looking at front, front left, front right
            possible_moves = ((self.row + self.index, self.col), (self.row + self.index, self.col - 1),
                              (self.row + self.index, self.col + 1))

        for i, move in enumerate(possible_moves):
            row, col = move
            if 0 <= row < 8 and 0 <= col < 8:
                thing = bo.get_piece(row, col)
                is_node = bo.check_node((row, col))
                thing_row, thing_col = thing.row, thing.col
                if is_node and i == 0:
                    valid_moves.append(move)
                if is_node and i == 1 and self.first_move:
                    valid_moves.append(move)
                if not is_node and thing_col != self.col and thing.color != self.color:
                    valid_moves.append(move)

        return valid_moves

    def __str__(self):
        return f"Pawn({self.row}, {self.col}, {self.color})"


class Rook(Piece):

    def __init__(self, color, row, col):
        super().__init__(color, row, col)

        self.image = self.IMAGES['rook'][self.color]
        self.castle = False
        self.index = -1 if self.color == 'white' else 1

    def valid_move(self, bo):
        """
        The directions that will be used in this code block are defined the way they are because of the following
        reason. In pygame, the origin is the left top corner. Because of that, the 8th row (7th for python) is the
        bottom row of the chess board. So if we want to go:

            -up: we need to go as nearest as possible to the 0th row (that is way we put max, because if there is a
                 piece before the 0th row, we can't pass the piece).

            -down: the goal is to go as nearest as possible to the 7th row. We put min because if there is a piece
                   before the 7th row, we will not pass.

            -left: same
            -right: same

        Since the position we want to filter in order to become a valid move must be in the square delimited by
        this directions, we need to define very well this square.  The directions that are defined by min will be 0
        (min movement) if they are empty. The directions defined by max will be 7 (max movement) if they are empty.
        With this definition, we will get the right valid moves even if there are no pieces in between.

        :param bo: Board
        :return: None
        """

        possible_moves = [(self.row + k, self.col) for k in range(-8, 8)
                          if (self.row + k, self.col) != (self.row, self.col)]
        possible_moves += [(self.row, self.col + k) for k in range(-8, 8)
                           if (self.row, self.col + k) != (self.row, self.col)]

        pieces_in_the_way_list = bo.get_pieces_in_the_way(possible_moves, self.color)
        possible_moves_copy = possible_moves.copy()

        up_pieces, down_pieces, left_pieces, right_pieces = [], [], [], []
        for move in pieces_in_the_way_list:
            piece_row, piece_col = move
            if piece_row < self.row:
                up_pieces.append(piece_row)
            elif piece_row > self.row:
                down_pieces.append(piece_row)
            if piece_col < self.col:
                left_pieces.append(piece_col)
            elif piece_col > self.col:
                right_pieces.append(piece_col)

        max_left = max(left_pieces) if left_pieces else 0
        max_right = min(right_pieces) if right_pieces else 7
        max_up = max(up_pieces) if up_pieces else 0
        max_down = min(down_pieces) if down_pieces else 7

        same_color, _ = bo.get_all_pieces_positions(self.color)
        for move in possible_moves_copy:
            row, col = move
            if max_up <= row <= max_down and max_left <= col <= max_right and move not in same_color:
                continue
            possible_moves.remove(move)

        return possible_moves

    def __str__(self):
        return f"Rook({self.row}, {self.col}, {self.color})"


class Queen(Piece):

    def __init__(self, color, row, col):
        super().__init__(color, row, col)

        self.image = self.IMAGES['queen'][self.color]

    def valid_move(self, bo):
        possible_moves = (Bishop(self.color, self.row, self.col).valid_move(bo)
                          + Rook(self.color, self.row, self.col).valid_move(bo))
        return possible_moves

    def __str__(self):
        return f"Queen({self.row}, {self.col}, {self.color})"


class King(Piece):

    def __init__(self, color, row, col):
        super().__init__(color, row, col)

        self.image = self.IMAGES['king'][self.color]
        self.castle = False

    def valid_move(self, bo):
        possible_moves = [(self.row - 1, self.col), (self.row + 1, self.col), (self.row, self.col - 1),
                          (self.row, self.col + 1), (self.row - 1, self.col + 1), (self.row - 1, self.col - 1),
                          (self.row + 1, self.col - 1), (self.row + 1, self.col + 1)]

        possible_moves_copy = possible_moves.copy()
        same_color, _ = bo.get_all_pieces_positions(self.color)
        for move in possible_moves_copy:
            row, col = move
            if 0 <= row <= 7 and 0 <= col <= 7 and move not in same_color:
                continue
            possible_moves.remove(move)

        return possible_moves

    def castle_move(self, bo):

        rook_positions = {'white': {'short': (7, 7), 'long': (7, 0)},
                          'black': {'short': (0, 7), 'long': (0, 0)}}

        king_positions = {'white': (7, 4), 'black': (0, 4)}

        rook_to_castle = rook_positions[self.color]
        row_short, col_short = rook_to_castle['short']
        row_long, col_long = rook_to_castle['long']

        try:
            short_castle_possible = not bo.get_piece(row_short, col_short).castle
        except:
            short_castle_possible = False

        try:
            long_castle_possible = not bo.get_piece(row_long, col_long).castle
        except:
            long_castle_possible = False

        # max long squares = 3, max short squares = 2
        long_squares = []
        short_squares = []

        castle_king_positions = [(rook_to_castle['short'][0], rook_to_castle['short'][1] - 1),
                                 (rook_to_castle['long'][0], rook_to_castle['long'][1] + 2)]

        _, diff_color = bo.get_all_pieces_positions(self.color)
        king_row, king_col = king_positions[self.color]
        for col in range(1, 7):
            if col != king_col:
                for (r, c) in diff_color:
                    for move in bo.get_piece(r, c).valid_move(bo):
                        if move == (king_row, col):
                            return []

                if not bo.check_node((king_row, col)):
                    if col < king_col:
                        long_squares.append(False)
                    else:
                        short_squares.append(False)
                else:
                    if col < king_col:
                        long_squares.append(True)
                    else:
                        short_squares.append(True)

        if all(short_squares) and all(long_squares) and short_castle_possible and long_castle_possible:
            return castle_king_positions
        if all(short_squares) and not all(long_squares) and short_castle_possible:
            return [castle_king_positions[0]]
        if not all(short_squares) and all(long_squares) and long_castle_possible:
            return [castle_king_positions[1]]
        if all(short_squares) and all(long_squares) and short_castle_possible:
            return [castle_king_positions[0]]
        if all(short_squares) and all(long_squares) and long_castle_possible:
            return [castle_king_positions[1]]
        return []

    def __str__(self):
        return f"King({self.row}, {self.col}, {self.color})"


class Bishop(Piece):

    def __init__(self, color, row, col):
        super().__init__(color, row, col)

        self.image = self.IMAGES['bishop'][self.color]

    def __str__(self):
        return f"Bishop({self.row}, {self.col}, {self.color})"

    def valid_move(self, bo):
        """
        The idea is the same as the tower but know the possible moves are different. The bishop moves along the
        diagonals, so the criteria to determinate if there is a piece in the way (making impossible
        to continue along the same diagonal as the piece) changes.

        We have calculated the pieces along the four diagonals the bishop has access to:

            - top_right_diagonal. The max position in which the bishop can stand will be determined by the
                                  min column to the right and the max row.
            - The same reason for the others.
        :param bo: Board
        :return: list
        """

        possible_moves = [(self.row + k, self.col + k) for k in range(-8, 8)
                          if (self.row + k, self.col + k) != (self.row, self.col)]
        possible_moves += [(self.row + k, self.col - k) for k in range(-8, 8)
                           if (self.row + k, self.col - k) != (self.row, self.col)]
        possible_moves_copy = possible_moves.copy()

        pieces_in_the_way_list = bo.get_pieces_in_the_way(possible_moves, self.color)

        right_top_diagonal, left_top_diagonal, right_bottom_diagonal, left_bottom_diagonal = [], [], [], []
        max_top_right_col, max_top_left_col, max_bottom_right_col, max_bottom_left_col = [], [], [], []

        for move in pieces_in_the_way_list:
            row, col = move
            # we check the diagonal where the position belongs.
            if row < self.row and col > self.col:
                right_top_diagonal.append(row)
                max_top_right_col.append(col)
            elif row < self.row and col < self.col:
                left_top_diagonal.append(row)
                max_top_left_col.append(col)
            elif row > self.row and col > self.col:
                right_bottom_diagonal.append(row)
                max_bottom_right_col.append(col)
            elif row > self.row and col < self.col:
                left_bottom_diagonal.append(row)
                max_bottom_left_col.append(col)

        """
        In the next block we are getting the limits of the bishop's movement. The top left and top right 
        will be the maximum because for pygame up is bottom. The left and the right bottom diagonals use min. 
        """
        max_top_left = max(left_top_diagonal) if left_top_diagonal else 0
        max_top_right = max(right_top_diagonal) if right_top_diagonal else 0
        min_bottom_left = min(left_bottom_diagonal) if left_bottom_diagonal else 7
        min_bottom_right = min(right_bottom_diagonal) if right_bottom_diagonal else 7

        col_top_right = min(max_top_right_col) if max_top_right_col else 7
        col_top_left = max(max_top_left_col) if max_top_left_col else 0
        col_bottom_right = min(max_bottom_right_col) if max_bottom_right_col else 7
        col_bottom_left = max(max_bottom_left_col) if max_bottom_left_col else 0

        same_color, _ = bo.get_all_pieces_positions(self.color)

        for move in possible_moves_copy:
            row, col = move
            condition = None
            if 0 <= col <= 7 and 0 <= row <= 7 and move not in same_color:
                # check top right, top left, bottom right, bottom left
                top_right = row < self.row and col > self.col
                top_left = row < self.row and col < self.col
                bottom_right = row > self.row and col > self.col
                bottom_left = row > self.row and col < self.col

                if top_right:
                    if max_top_right <= row and col <= col_top_right:
                        condition = True
                elif top_left:
                    if max_top_left <= row and col >= col_top_left:
                        condition = True
                elif bottom_right:
                    if row <= min_bottom_right and col <= col_bottom_right:
                        condition = True
                elif bottom_left:
                    if row <= min_bottom_left and col >= col_bottom_left:
                        condition = True
                if not condition:
                    possible_moves.remove((row, col))
            else:
                possible_moves.remove((row, col))

        return possible_moves


class Knight(Piece):

    def __init__(self, color, row, col):
        super().__init__(color, row, col)

        self.image = self.IMAGES['knight'][self.color]

    def valid_move(self, bo):
        possible_moves = [(self.row + 2, self.col + 1), (self.row + 2, self.col - 1),
                          (self.row - 2, self.col + 1), (self.row - 2, self.col - 1),
                          (self.row + 1, self.col + 2), (self.row + 1, self.col - 2),
                          (self.row - 1, self.col + 2), (self.row - 1, self.col - 2)]
        possible_moves_copy = possible_moves.copy()
        same_color, _ = bo.get_all_pieces_positions(self.color)

        for move in possible_moves_copy:
            row, col = move
            if 0 <= row <= 7 and 0 <= col <= 7 and move not in same_color:
                continue
            possible_moves.remove(move)

        return possible_moves

    def __str__(self):
        return f"Knight({self.row}, {self.col}, {self.color})"
