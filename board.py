import numpy as np
from pygame import draw
from piece import Piece
import pygame
from constants import BLACK, BRIGHT, HEIGHT, LIGHT_YELLOW, COLS, DARK, ROWS, SQUARE_SIZE, STATUS_BAR_COLOR, STATUS_BAR_HEIGHT, WHITE, WIDTH

class Board:
    def __init__(self):
        self.board_color = []
        self.board_pieces = []
        self.starting_list = []
        self.available_kills_len = 0
        self.pieces_player_len = 12
        self.pieces_opponent_len = 12
        self.color_board()
        self.create_board()


    #Board definition 1-black, 0-white
    def color_board(self):
        self.board_color = np.zeros((8,8),dtype=int)
        self.board_color[1::2,::2] = 1
        self.board_color[::2,1::2] = 1

    def create_board(self):
        self.board_pieces = ([], [], [], [], [], [], [], [])
        for i in range(8):
            for _ in range(8):
                self.board_pieces[i].append(None)
        for i in range(24):
            if i < 12:
                pos = self.starting_position(i)
                piece = Piece(i, pos[0], pos[1], "white", WHITE)
                self.board_pieces[pos[0]][pos[1]] = piece
                #print("ID: ", i, "column: ", piece.starting_col, "row: ", piece.starting_row ,"color: ", piece.color, " created")
            else:
                pos = self.starting_position(i)
                piece = Piece(i, pos[0], pos[1], "black", BLACK)
                self.board_pieces[pos[0]][pos[1]] = piece
                #print("ID: ", i, "column: ", piece.starting_col, "row: ", piece.starting_row ,"color: ", piece.color, " created")

    def starting_position(self, id): 
        index = 0
        for row in self.board_color:
            indey = 0
            for cell in row:
                if 0 <= index <= 2 or 5 <= index <= 7:
                    if cell == 1:
                        self.starting_list.append([index, indey])
                indey += 1
            index += 1

        return self.starting_list[id]

    def draw_board(self, window):
        window.fill(DARK)
        for row in range(ROWS):
            for col in range(COLS):
                if self.board_color[row][col] == 0:
                    pygame.draw.rect(window, BRIGHT, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                elif self.board_color[row][col] == 2: # Color spaces in different color (available spaces to move clicked pawn)
                    pygame.draw.rect(window, LIGHT_YELLOW, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.draw.rect(window, STATUS_BAR_COLOR, (0, HEIGHT, WIDTH, STATUS_BAR_HEIGHT))

    def draw_pieces(self, window):
        for row in range(8):
            for col in range(8):
                if self.board_pieces[row][col] is not None:
                    window.blit(pygame.transform.scale((self.board_pieces[row][col].image), (SQUARE_SIZE, SQUARE_SIZE)),
                                pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def is_piece(self, x, y):
        if self.board_pieces[y][x] is not None:
            return True
        else:
            return False

    def is_player_piece(self, x, y):
        if self.board_pieces[y][x] is not None:
            if self.board_pieces[y][x].color == 'black':
                return True
            else:
                return False
        else:
            return False

    def is_opponent_piece(self, x, y):
        if self.board_pieces[y][x] is not None:
            if self.board_pieces[y][x].color == 'white':
                return True
            else:
                return False
        else:
            return False

    def check_moves(self, x, y):
        moves = []
        
        # Check move to the left
        if x != 0 and y != 0:
            if not self.is_piece(x-1, y-1):
                moves.append((x-1, y-1))

        # Check move to the right
        if x != 7 and y != 0:
            if not self.is_piece(x+1, y-1):
                moves.append((x+1, y-1))

        return moves

    def check_super_moves(self, x, y):
        moves = self.check_moves(x,y) # Check regular moves to the top

        if x != 0 and y != 7:
            if not self.is_piece(x-1, y+1):
                moves.append((x-1, y+1))

        if x != 7 and y != 7:
            if not self.is_piece(x+1, y+1):
                moves.append((x+1, y+1))

        return moves

    def color_moves(self, moves):
        self.color_board() # Reset board colors
        for move in moves:
            self.board_color[move[0]][move[1]] = 2

    def check_kill(self, x, y):
        self.color_board() # Reset board colors

        kills = []
        
        # Check kill to the left
        if x > 1 and y > 1:
            if self.is_piece(x-1, y-1) and self.board_pieces[y-1][x-1].is_opponent_piece() and not self.is_piece(x-2, y-2):
                kills.append((x-2, y-2))

        # Check kill to the right
        if x < 6 and y > 1:
            if self.is_piece(x+1, y-1) and self.board_pieces[y-1][x+1].is_opponent_piece() and not self.is_piece(x+2, y-2):
                kills.append((x+2, y-2))

        return kills
    

    def check_super_kill(self, x, y):
        kills = self.check_kill(x, y) # Check regular kills to the top
        
        if x > 1 and y < 6:
            if self.is_piece(x-1, y+1) and self.board_pieces[y+1][x-1].is_opponent_piece() and not self.is_piece(x-2, y+2):
                kills.append((x-2, y+2))

        if x < 6 and y < 6:
            if self.is_piece(x+1, y+1) and self.board_pieces[y+1][x+1].is_opponent_piece() and not self.is_piece(x+2, y+2):
                kills.append((x+2, y+2))

        return kills


    def available_kills(self):
        kill_list = {}
        
        for x in range(8):
            for y in range(8):
                if self.is_piece(x, y) and self.board_pieces[y][x].is_player_piece():
                    if len(self.check_kill(x, y)) > 0: 
                        kill_list[(x, y)] = self.check_kill(x, y)

        self.available_kills_len = len(kill_list)

        return kill_list

    def available_super_kills(self):
        kill_list = {}
        
        for x in range(8):
            for y in range(8):
                if self.is_player_piece(x, y):
                    if len(self.check_super_kill(x, y)) > 0: 
                        kill_list[(x, y)] = self.check_super_kill(x, y)

        self.available_kills_len = len(kill_list)

        return kill_list

    def move_piece(self, start_x, start_y, dest_x, dest_y):
        self.board_pieces[dest_y][dest_x] = self.board_pieces[start_y][start_x]
        self.board_pieces[start_y][start_x] = None

        # Check if the piece should change to seper (king)
        piece = self.board_pieces[dest_y][dest_x]
        if dest_y == 0 and piece.color == 'black' or dest_y == 7 and piece.color == 'white':
            piece.make_super()

    def kill_piece(self, kill_list):
        for x, y in kill_list:
            if self.board_pieces[y][x].color == 'black':
                self.pieces_player_len -= 1
            else:
                self.pieces_opponent_len -= 1

            self.board_pieces[y][x] = None

    def make_super(self, x, y):
        self.board_pieces[y][x].make_super()

    def is_super(self, x, y):
        if self.board_pieces[y][x].super:
            return True
        else:
            return False
