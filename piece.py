from constants import SQUARE_SIZE, WHITE, WHITE_KING, BLACK_KING


class Piece:

    def __init__(self, id, row, col, color, image):
        self.id = id
        self.starting_row = row
        self.starting_col = col
        self.color = color
        self.image = image
        self.super = False
    
    def make_super(self):
        self.super = True
        if self.is_player_piece():
            self.image = BLACK_KING
        else:
            self.image = WHITE_KING
    
    def is_player_piece(self):
        if self.color == 'black':
            return True
        else:
            return False

    def is_opponent_piece(self):
        if self.color == 'white':
            return True
        else:
            return False

    def is_super(self):
        return self.super
