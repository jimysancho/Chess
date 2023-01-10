from .PiecesClasses import *


class Node:

    def __init__(self, row, col):
        """
        :param row: int
        :param col: int

        width and height are calculated in the main file. It corresponds to SQUARE_WIDTH and SQUARE_HEIGHT
        """
        self.row = row
        self.col = col

    def __str__(self):
        return f"Node({self.row}, {self.col})"

    def draw(self, window):
        pass


class Board:

    ROWS = 8
    COLS = 8

    type_of_initial_pieces = {(6, i): Pawn for i in range(COLS)}

    type_of_initial_pieces[(7, 0)] = Rook
    type_of_initial_pieces[(7, 1)] = Knight
    type_of_initial_pieces[(7, 2)] = Bishop
    type_of_initial_pieces[(7, 3)] = Queen
    type_of_initial_pieces[(7, 4)] = King
    type_of_initial_pieces[(7, 5)] = Bishop
    type_of_initial_pieces[(7, 6)] = Knight
    type_of_initial_pieces[(7, 7)] = Rook

    type_pieces = {'Rook': Rook, 'Bishop': Bishop, 'Queen': Queen, 'Knight': Knight}

    color = {6: "white", 7: "white", 0: "black", 1: "black"}

    def __init__(self):

        self.grid = [[Node(j, i) for i in range(self.COLS)] for j in range(self.ROWS)]

        for j in (0, 1, 6, 7):
            for i in range(self.COLS):
                if j == 1:
                    k = j + 5
                elif j == 0:
                    k = j + 7
                else:
                    k = j
                self.grid[j][i] = self.type_of_initial_pieces[(k, i)](self.color[j], j, i)

        self.occupied_positions = set()
        for row in self.grid:
            for piece in row:
                r, c = piece.row, piece.col
                if not self.check_node((r, c)):
                    self.occupied_positions.add((r, c))

    def __repr__(self):
        output = [[] for _ in range(self.ROWS)]
        for row, lst in zip(self.grid, output):
            for node in row:
                lst.append(str(node))

        str_output = ""
        for line in output:
            line = str(line)
            str_output += line
            str_output += "\n"

        return str_output

    def get_piece(self, row, col):
        """
        :param row: int
        :param col: int
        :return: Piece of Node class
        """
        return self.grid[row][col]

    def check_node(self, position):
        """
        We ask if some position is occupied. If not, this will mean a node is the position, so we will return
        True.
        :param position: tuple
        :return: bool
        """
        row, col = position
        thing = self.get_piece(row, col)
        if type(thing) is Node:
            return True
        return False

    def check_move(self, position_to_move, old_position, check_comprobation=False, castle=False):
        """
        This method will change the necessary information in order to update the visual board, making possible
        to move the pieces
        :param position_to_move: tuple
        :param old_position: tuple
        :param check_comprobation: bool
        :param castle: bool
        :return: None
        """

        if castle:
            new_row, new_col = position_to_move
            king_row, king_col = old_position
            rook_row, rook_col = new_row, 5 if new_col == 6 else 3
            rook = self.get_piece(new_row, 0) if new_col == 2 else self.get_piece(new_row, 7)
            king = self.get_piece(king_row, king_col)

            self.grid[rook.row][rook.col] = Node(rook.row, rook.col)
            self.grid[new_row][new_col] = king
            self.grid[king_row][king_col] = Node(king_row, king_col)

            rook.row, rook.col = rook_row, rook_col
            king.row, king.col = new_row, new_col

            self.grid[rook_row][rook_col] = rook
            self.grid[new_row][new_col].recalculate_distance(position_to_move)
            self.grid[rook_row][rook_col].recalculate_distance((rook_row, rook_col))

            self.occupations()

        else:
            new_row, new_col = position_to_move
            old_row, old_col = old_position

            original = self.get_piece(new_row, new_col)

            old_thing = self.get_piece(old_row, old_col)
            new_thing = old_thing

            if type(old_thing) is Pawn and not check_comprobation:
                if old_thing.first_move:
                    new_thing.first_move = False

            new_thing.row, new_thing.col = new_row, new_col
            old_thing = Node(old_row, old_col) if not check_comprobation else original

            self.grid[new_row][new_col] = new_thing
            self.grid[old_row][old_col] = old_thing

            self.grid[new_row][new_col].recalculate_distance(position_to_move)
            self.occupations()

    def occupations(self):
        """
        With this method we will get all the occupied positions on the board. Very important to put the
        first line of code to reset the set.
        :return: None
        """
        self.occupied_positions = set()
        for row in self.grid:
            for piece in row:
                if not self.check_node((piece.row, piece.col)):
                    self.occupied_positions.add((piece.row, piece.col))

    def get_all_pieces_positions(self, color):
        """
        Given a color, we will separate the occupied positions of the board in same color positions (these are the
        positions occupied by pieces of the same color) and different color positions (positions occupied by different
        color pieces)
        :param color: str
        :return: tuple of lists
        """
        occupied = self.occupied_positions
        same_color = set()
        diff_color = set()
        for position in occupied:
            row, col = position
            piece = self.get_piece(row, col)
            if piece.color == color:
                same_color.add((row, col))
            else:
                diff_color.add((row, col))
        return same_color, diff_color

    def get_pieces_in_the_way(self, possible_moves, color):
        """
        Given a color, and a list of possible moves, we will return the pices in the way, that is, the pieces on
        a possible move (in the list of possible_moves).
        :param possible_moves: list
        :param color: str
        :return: lst
        """
        same_color_positions, different_color_positions = self.get_all_pieces_positions(color)
        pieces_in_the_way_set = (same_color_positions | different_color_positions) & set(possible_moves)
        pieces_in_the_way_list = list(pieces_in_the_way_set)

        return pieces_in_the_way_list
