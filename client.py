import pygame
from constants import SQUARE_SIZE, STATUS_BAR_HEIGHT, STATUS_COLOR, WIDTH, HEIGHT, ROWS, COLS
from board import Board
from network import Network
from sys import argv
from time import sleep

def clicked_pos(position):
    return int(position[0]/(WIDTH/ROWS)), int(position[1]/(HEIGHT/COLS))

def flip_coords(x, y):
    # Function to flip coords before sending data to opponent
    # e.g (0,0) -> (7,7), (2,4) -> (5,3) 
    return abs(7 - x), abs(7 - y)

def flip_coords_list(list):
    flipped = []
    for item in range(len(list)):
        flipped.append(flip_coords(list[item][0], list[item][1]))

    return flipped

def turn(x, y, piece_clicked):
    global my_turn
    available_kills = board.available_kills()
    print("kill list: ", available_kills)

    available_super_kills = board.available_super_kills()
    print("kill list: ", available_kills)

    if not piece_clicked: # When user is going to click a pawn
        if board.is_piece(x, y) and board.board_pieces[y][x].is_player_piece():
            if board.is_super(x, y):
                if len(available_super_kills) == 0: # No kills are available
                    # Piece clicked
                    moves = board.check_super_moves(x, y) # moves - tuple containing available moves - x,y coords
                    board.color_moves(moves)
                else: # kill is available
                    if (x, y) in available_super_kills:
                        moves = available_super_kills[(x, y)] # moves - tuple containing available moves - x,y coords   
                        board.color_moves(moves)
                    else:
                        return None # There are available kills but wrong pawn was clicked
            else:
                if len(available_kills) == 0: # No kills are available
                    # Piece clicked
                    moves = board.check_moves(x, y) # moves - tuple containing available moves - x,y coords
                    board.color_moves(moves)
                else: # kill is available
                    if (x, y) in available_kills:
                        moves = available_kills[(x, y)] # moves - tuple containing available moves - x,y coords   
                        board.color_moves(moves)
                    else:
                        return None # There are available kills but wrong pawn was clicked
            return {'coords': (x, y), 'moves': moves, 'init_coords': (x, y), 'to_kill': []}
        else:
            # Piece not clicked
            return None
    else:
        if board.is_piece(x, y) and len(piece_clicked['to_kill']) == 0: # when user hasnt killed any pieces in the current turn
            if piece_clicked['coords'][0] == x and piece_clicked['coords'][1] == y:
                # Piece unclicked
                board.color_board()
                return None        
            elif board.is_piece(x, y) and board.board_pieces[y][x].is_player_piece():
                # Change to other piece
                return turn(x, y, None)
            else:
                # User clicked opponent pawn
                board.color_board()
                return None
        elif board.is_piece(x, y) == False:

            
            if board.is_super(*piece_clicked['coords']):
                if len(available_super_kills) == 0: # player doesnt have possibility of killing
                    if (x, y) in piece_clicked['moves']:
                        board.color_board()
                        board.move_piece(*piece_clicked['coords'], x, y)
                        network.send((*flip_coords(*piece_clicked['coords']), *flip_coords(x, y)))
                        my_turn = False
                        return None
                    else:
                        board.color_moves(piece_clicked['moves'])
                        return piece_clicked
                else: #player has to kill piece
                    if (x, y) in available_super_kills[piece_clicked['coords']]: 
                        x_killed = (piece_clicked['coords'][0] + x)/2
                        y_killed = (piece_clicked['coords'][1] + y)/2
                        board.kill_piece([[int(x_killed), int(y_killed)]])

                        print("x_killed", x_killed, "y_killed", y_killed)

                        piece_clicked['to_kill'].append([int(x_killed),int(y_killed)])
                        board.move_piece(*piece_clicked['coords'], x, y)
                        available_super_kills = board.available_super_kills()
                        if (x, y) in available_super_kills:
                            piece_clicked['coords'] = (x, y)
                            piece_clicked['moves'] = available_super_kills[(x, y)]
                            board.color_moves(piece_clicked['moves'])
                            return piece_clicked
                        else:
                            network.send((*flip_coords(*piece_clicked['init_coords']), *flip_coords(x, y), flip_coords_list(piece_clicked['to_kill']))) #added killed pieces coords (list) in send data
                            my_turn = False
                            return None
                    else:
                        board.color_moves(piece_clicked['moves'])
                        return piece_clicked

            else:
                if len(available_kills) == 0: # player doesnt have possibility of killing
                    if (x, y) in piece_clicked['moves']:
                        board.color_board()
                        board.move_piece(*piece_clicked['coords'], x, y)
                        network.send((*flip_coords(*piece_clicked['coords']), *flip_coords(x, y)))
                        my_turn = False
                        return None
                    else:
                        board.color_moves(piece_clicked['moves'])
                        return piece_clicked
                else: #player has to kill piece
                    if (x, y) in available_kills[piece_clicked['coords']]: 
                        x_killed = (piece_clicked['coords'][0] + x)/2
                        y_killed = (piece_clicked['coords'][1] + y)/2
                        board.kill_piece([[int(x_killed), int(y_killed)]])

                        print("x_killed", x_killed, "y_killed", y_killed)

                        piece_clicked['to_kill'].append([int(x_killed),int(y_killed)])
                        board.move_piece(*piece_clicked['coords'], x, y)
                        available_kills = board.available_kills()
                        if (x, y) in available_kills:
                            piece_clicked['coords'] = (x, y)
                            piece_clicked['moves'] = available_kills[(x, y)]
                            board.color_moves(piece_clicked['moves'])
                            return piece_clicked
                        else:
                            network.send((*flip_coords(*piece_clicked['init_coords']), *flip_coords(x, y), flip_coords_list(piece_clicked['to_kill']))) #added killed pieces coords (list) in send data
                            my_turn = False
                            return None
                    else:
                        board.color_moves(piece_clicked['moves'])
                        return piece_clicked

        else:
            # Not Moved
            board.color_moves(piece_clicked['moves'])
            return piece_clicked

def status_display(status):
    font = pygame.font.Font('freesansbold.ttf', 12)
    textSurface = font.render(status, True, STATUS_COLOR)
    textRect = textSurface.get_rect()
    textRect.center = (WIDTH // 2, HEIGHT+STATUS_BAR_HEIGHT//2)
    WINDOW.blit(textSurface, textRect)

def main():
    global board, my_turn

    my_turn = network.connect()
    
    if my_turn:
        _ = network.recive()

    status = ''
    send = False
    run = True
    piece_clicked = None

    while run:
        clock.tick(FPS)

        if board.pieces_player_len == 0: # Opponent win
            run = False
            status = 'Opponent wins'
            
        elif board.pieces_opponent_len == 0: # Player win
            run = False
            status = 'You win'

        if board.available_kills_len > 0:
            status = 'You have to kill!'

        board.draw_board(WINDOW)
        board.draw_pieces(WINDOW)
        if(piece_clicked):
            pygame.draw.circle(WINDOW, (255,255,255), (piece_clicked['coords'][0]*SQUARE_SIZE+SQUARE_SIZE/2, 
                                                       piece_clicked['coords'][1]*SQUARE_SIZE+SQUARE_SIZE/2), 10)
        status_display(status)
        pygame.display.update()

        if my_turn == False:
            status = 'Opponent\'s turn!'
            data_recive = network.recive()
            
            if data_recive is not None and len(data_recive) > 0:
                board.move_piece(data_recive[0], data_recive[1], data_recive[2], data_recive[3])
                if len(data_recive) > 4:
                    board.kill_piece(data_recive[4])
                my_turn = True
        else: status = 'Your turn!'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                network.disconnect()
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if my_turn == True:
                    pos = pygame.mouse.get_pos()
                    if(pos[1] < HEIGHT):
                        x, y =  clicked_pos(pos)
                        print("X: "+ str(x) + ' Y: ' + str(y))
                        piece_clicked = turn(x, y, piece_clicked)
                        print('Piece clicked: '+str(piece_clicked))
                    else:
                        pass

    sleep(5)
    network.disconnect()
    pygame.quit()
    quit()

if __name__ == '__main__':
    '''
    consts for window
    '''
    FPS = 15
    programIcon = pygame.image.load('assets/icon.png')

    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT+STATUS_BAR_HEIGHT))
    pygame.display.set_caption('Warcaby')
    pygame.display.set_icon(programIcon)
    pygame.font.init()

    '''
    Game global variables
    '''
    clock = pygame.time.Clock()
    board = Board()
    my_turn = None

    network = Network(argv) # argv - arguments passed in console (ip address in our case)
    main()
