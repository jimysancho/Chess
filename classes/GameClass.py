class Game:

    def __init__(self, board, piece=None):
        self.board = board

        self.color = "white"
        self.piece = piece

        self.current_valid_moves = []

        self.kings_positions = {'white': None, 'black': None}
        for row in self.board.grid:
            for piece in row:
                if "King" in repr(piece):
                    self.kings_positions[piece.color] = (piece.row, piece.col)

    def change_turn(self):
        """
        This method allows to change turns in the game.
        :return: None
        """
        turns = {'white': 'black', 'black': 'white'}
        self.color = turns[self.color]

    def check_turn(self):
        """
        This method checks the turn to play, not allowing to play two moves in a row.
        :return: bool
        """
        if self.piece.color == self.color:
            return True
        return False

    def reset(self):
        """
        This method unselect the piece.
        :return: None
        """
        self.piece = None
        self.current_valid_moves = []

    @property
    def return_valid_moves(self):
        """
        This method returns the valid moves of the selected piece.
        :return: list
        """
        return self.piece.valid_move(self.board)

    def move(self, new_position):
        """
        We move the selected piece. It allows to castle as well and if the king is under attack
        it does not allow to move the piece.
        :param new_position: tuple
        :return: None, Piece, tuple
        """
        new_row, new_col = new_position
        row, col = self.piece.row, self.piece.col

        if (row, col) == self.kings_positions[self.color]:
            castles_moves = self.piece.castle_move(self.board)
            if (new_row, new_col) in castles_moves and not self.piece.castle:
                king_under_attack = self.is_king_under_attack(new_position, (row, col))
                if not king_under_attack:
                    self.board.check_move((new_row, new_col), (row, col), castle=True)
                    self.check_castle()
                    self.change_turn()
                    self.reset()
                    return

        if (new_row, new_col) in self.current_valid_moves[:]:
            king_under_attack = self.is_king_under_attack(new_position, (row, col))
            protected_king = self.protect_king(new_position, (row, col))

            if not king_under_attack and protected_king:
                eaten = not self.board.check_node((new_row, new_col))
                old_piece = self.board.get_piece(new_row, new_col)
                self.board.check_move((new_row, new_col), (row, col))
                self.check_castle()
                self.change_turn()
                self.reset()
                if eaten:
                    return old_piece
        return new_row, new_col

    def select_piece(self, row, col, x, y):
        """
        If the selected piece matches the turn (by color), we select it.
        :param row: int
        :param col: int
        :param x: float
        :param y: float
        :return: (tuple, list), (None, list)
        """
        if not self.board.check_node((row, col)):
            self.piece = self.board.get_piece(row, col)
            condition = self.check_turn()
            if condition:
                self.current_valid_moves = self.return_valid_moves
                return (x, y, row, col), self.current_valid_moves
            self.reset()
        self.reset()
        return None, []

    def is_king_under_attack(self, new_position, old_position):
        """
        With this method we check if by moving a piece, the king will be attacked. If this is the case, the
        method will return False, else True.

        :param new_position: tuple. Position to move the selected piece
        :param old_position: tuple. Initial position of the piece.
        :return: bool
        """
        self.board.check_move(new_position, old_position, True)
        if self.check_to_king():
            self.board.check_move(old_position, new_position, True)
            return True
        self.board.check_move(old_position, new_position, True)
        return False

    def check_to_king(self):
        """
        This method checks if the king is under attack.
        :return: bool
        """
        # this line of code is very important because is the one that allows to see the future outcome
        self.track_kings()

        king_pos = self.kings_positions[self.color]
        _, different_color = self.board.get_all_pieces_positions(self.color)

        for (row, col) in different_color:
            piece = self.board.get_piece(row, col)
            valid_moves = piece.valid_move(self.board)
            for move in valid_moves:
                if move == king_pos:
                    return True
        return False

    def protect_king(self, new_position, old_position):
        """
        If we are on check, we need to protect the king in order for a move to be valid. If by moving
        the selected piece we protect the king this method returns True, else false.
        :param new_position: tuple
        :param old_position: tuple
        :return: bool
        """
        check = self.check_to_king()
        if check:
            self.board.check_move(new_position, old_position, True)
            if self.check_to_king():
                self.board.check_move(old_position, new_position, True)
                return False
            self.board.check_move(old_position, new_position, True)
        return True

    def track_kings(self):
        """
        This method tracks the positions of the kings.
        :return: None
        """
        for row in self.board.grid:
            for piece in row:
                if "King" in str(piece):
                    self.kings_positions[piece.color] = (piece.row, piece.col)

    def promote(self, piece_string, col):
        """
        With this method we change the promoted pawn to a piece of interest.
        :param piece_string: str
        :param col: int
        :return:
        """
        type_of_piece = self.board.type_pieces[piece_string]
        row = 0 if self.color == 'black' else 7
        self.piece = type_of_piece('white' if self.color == 'black' else 'black', row, col)

        self.board.grid[row][col] = type_of_piece('white' if self.color == 'black' else 'black', row, col)
        self.board.occupations()
        self.reset()

    def any_promotion(self):
        """
        This method checks if any pawn has reached the final row. If this is the case we return True and the
        piece information else None.
        :return:
        """
        for row in (self.board.grid[0], self.board.grid[7]):
            for piece in row:
                if "Pawn" in str(piece):
                    if piece.color == 'white':
                        if piece.row == 0:
                            return True, piece.row, piece.col
                    else:
                        if piece.row == 7:
                            return True, piece.row, piece.col
        return

    def check_castle(self):
        """
        This method checks if the king has been castled.
        :return: None
        """
        if "Rook" in str(self.piece) or "King" in str(self.piece):
            self.piece.castle = True

    def check_mate(self):
        same_color, _ = self.board.get_all_pieces_positions(self.color)
        other_color = 'black' if self.color == 'white' else 'white'
        for (row, col) in same_color:
            piece = self.board.get_piece(row, col)
            valid_moves = piece.valid_move(self.board)
            for move in valid_moves:
                if self.protect_king(move, (piece.row, piece.col)):
                    return None
        return other_color

    @staticmethod
    def another_game(pressed_key):
        if pressed_key == 768:
            return True
        return False
