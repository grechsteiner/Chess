# Full GUI Chess Game
# Custom AI opponent with several difficulty options
# Implements alpha-beta pruning and other algorithm optimizations to minimize AI best move search time
# First iteration was written as the final project for my Grade 12 (2022) computer science course, but I continued 
# to refine the existing features and add more functionality as a side project


import pygame, os, random, copy, time
from pygame.locals import *
from pygame import gfxdraw


# Window width & height constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# Colour constants
BLACK_COLOUR = (0, 0, 0)
WHITE_COLOUR = (255, 255, 255)
TAN_COLOUR = (230, 220, 170)
LIME_COLOUR = (50 ,205, 50)
GRAY_COLOUR = (169, 169, 169)
WHITE_TURN_COLOUR = (245,245,220)
GREEN_COLOUR = (0,100,0)
RED_COLOUR = (255,0,0)
DARK_GRAY_COLOUR = (128,138,135)
LIGHT_GRAY_COLOUR = (224,238,238)
MENU_GRAY_COLOUR = (193,205,205)
DARK_BEIGE_COLOUR = (205,183,158)
LIGHT_BEIGE_COLOUR = (245,245,220)
MENU_BEIGE_COLOUR = (255,228,196)

# "Team" constants
BLACK = 0
WHITE = 1

# Piece constants
ROOK = 0
KNIGHT = 1
BISHOP = 2
QUEEN = 3
KING = 4
PAWN = 5

# AI difficulty constants
EASY = 1
MEDIUM = 2
HARD = 3

# Menu option constants
AI_EASY = 0
AI_MEDIUM = 1
AI_HARD = 2
TWO_PLAYER = 3
HOW_TO_PLAY = 4
EXIT = 5
DESELECT_SINGLE_PLAYER = 6

# Neighbour constants for a given piece on the board
ON_RIGHT = 0
ON_LEFT = 1
NO_NEIGHBOUR = 2

# Height/width of the board constant
SIZE = 8


def terminate():
    """Called when the user closes the window or presses the ESC key, terminates the program"""
    pygame.quit()
    os._exit(1)
    

def draw_text(text, font, surface, x, y, textcolour):
    """Draws the text on the surface, starting at the specified location"""
    textobj = font.render(text, 1, textcolour)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def draw_text_middle(text, font, surface, x, y, textcolour):
    """Draws the text on the surface, centered at the specified location"""
    textobj = font.render(text, 1, textcolour)
    textrect = textobj.get_rect()
    textrect.midtop = (x, y)
    surface.blit(textobj, textrect)


def load_image(filename):
    """Loads image from specified file, returns said image and corresponding rectangle"""
    image = pygame.image.load(filename)
    image = image.convert_alpha()
    return image


def create_2D_array(rows, cols, value):
    """Creates and returns 2D array of inputted dimensions, each cell is set to input value"""
    array = [[value for x in range(cols)] for y in range(rows)]
    return array


def opposite_colour(colour):
    """Returns the opposite colour to that of the input colour"""
    if colour == BLACK:
        return WHITE
    else:
        return BLACK


def draw_border_lines(windowSurface, top, bottom, left, right, lightcolour, darkcolour):                      
    """Used for drawing lines around rectangle for 3D effect"""

    # Light colour, top and left of rectangle
    pygame.draw.line(windowSurface, lightcolour, (left, top-1), (right, top-1))
    pygame.draw.line(windowSurface, lightcolour, (left, top-2), (right+1, top-2))
    pygame.draw.line(windowSurface, lightcolour, (left-1, top-2), (left-1, bottom))
    pygame.draw.line(windowSurface, lightcolour, (left-2, top-2), (left-2, bottom+1))

    # Dark colour, bottom and right of rectangle
    pygame.draw.line(windowSurface, darkcolour, (right+1, top-1), (right+1, bottom+2))
    pygame.draw.line(windowSurface, darkcolour, (right+2, top-2), (right+2, bottom+2))
    pygame.draw.line(windowSurface, darkcolour, (left-1, bottom+1), (right, bottom+1))
    pygame.draw.line(windowSurface, darkcolour, (left-2, bottom+2), (right, bottom+2))


def display_instructions(windowSurface, homeicon, hinticon, soundicon, menuhomeicon):
    """Displays the instructions page"""

    # Fill background
    windowSurface.fill(TAN_COLOUR)

    # Display home icon
    windowSurface.blit(homeicon.image, homeicon.rect)

    # Set up fonts
    titleFont = pygame.font.SysFont("Times New Roman", 90, italic=True)
    headerFont = pygame.font.SysFont("Times New Roman", 40)
    basicFont = pygame.font.SysFont("Times New Roman", 30)

    # Draw title
    draw_text_middle("How To Play", titleFont, windowSurface, windowSurface.get_rect().centerx, 5, BLACK_COLOUR)

    # Display buttons
    windowSurface.blit(hinticon.image, hinticon.rect)
    windowSurface.blit(soundicon.image, soundicon.rect)
    windowSurface.blit(menuhomeicon.image, menuhomeicon.rect)

    # Display buttons text
    draw_text("Buttons:", headerFont, windowSurface, 100, 150, BLACK_COLOUR)
    draw_text("Returns to main menu", basicFont, windowSurface, 140, 200, BLACK_COLOUR)
    draw_text("Toggles sound effects on/off", basicFont, windowSurface, 140, 240, BLACK_COLOUR)
    draw_text("Displays a hint", basicFont, windowSurface, 140, 280, BLACK_COLOUR)

    # Display controls text
    draw_text("Controls:", headerFont, windowSurface, 100, 350, BLACK_COLOUR)
    draw_text("- All user input is through clicks", basicFont, windowSurface, 100, 400, BLACK_COLOUR)
    draw_text("- Click on piece to select or unselect it", basicFont, windowSurface, 100, 440, BLACK_COLOUR)
    draw_text("- Legal moves will be displayed with green circles", basicFont, windowSurface, 100, 480, BLACK_COLOUR)
    draw_text("- Click on square you wish to move piece to", basicFont, windowSurface, 100, 520, BLACK_COLOUR)
   
    # Update screen
    pygame.display.update()


def process_instructions():
    """Respond to keyboard and mouse clicks when on instructions screen"""

    # Continue in loop until option is chosen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
                #Clicked the home button, return to main menu
                if (event.pos[0] >= 960 and event.pos[0] < 995
                and event.pos[1] >= 5 and event.pos[1] < 40):
                    return
                

def display_menu(windowSurface, bigbishop, bigknight):
    """Displays the main menu and its options"""

    # Fill background
    windowSurface.fill(TAN_COLOUR)

    # Set up fonts
    basicFont = pygame.font.SysFont("Arial", 40)
    titleFont = pygame.font.SysFont("Times New Roman", 170, italic=True)

    # Draw title
    draw_text_middle("Chess", titleFont, windowSurface, windowSurface.get_rect().centerx, 1, BLACK_COLOUR)

    # Draw rectangles to be clicked on                                     
    pygame.draw.rect(windowSurface, MENU_GRAY_COLOUR, (windowSurface.get_rect().centerx - 125, 215, 250, 60))                                      
    pygame.draw.rect(windowSurface, MENU_GRAY_COLOUR, (windowSurface.get_rect().centerx - 125, 285, 250, 60))
    pygame.draw.rect(windowSurface, MENU_GRAY_COLOUR, (windowSurface.get_rect().centerx - 125, 355, 250, 60))                                      
    pygame.draw.rect(windowSurface, MENU_GRAY_COLOUR, (windowSurface.get_rect().centerx - 125, 425, 250, 60))
    
    # Draw options to click on
    draw_text_middle("Single Player", basicFont, windowSurface, windowSurface.get_rect().centerx, 220, BLACK_COLOUR)
    draw_text_middle("Two Player", basicFont, windowSurface, windowSurface.get_rect().centerx, 290, BLACK_COLOUR)
    draw_text_middle("How To Play", basicFont, windowSurface, windowSurface.get_rect().centerx, 360, BLACK_COLOUR)
    draw_text_middle("Exit", basicFont, windowSurface, windowSurface.get_rect().centerx, 430, BLACK_COLOUR)

    # Draw lines around rectangles for 3d effect
    draw_border_lines(windowSurface, 215, 274, windowSurface.get_rect().centerx - 125, windowSurface.get_rect().centerx + 124,
                      LIGHT_GRAY_COLOUR, DARK_GRAY_COLOUR)
    draw_border_lines(windowSurface, 285, 344, windowSurface.get_rect().centerx - 125, windowSurface.get_rect().centerx + 124,
                      LIGHT_GRAY_COLOUR, DARK_GRAY_COLOUR)
    draw_border_lines(windowSurface, 355, 414, windowSurface.get_rect().centerx - 125, windowSurface.get_rect().centerx + 124,
                      LIGHT_GRAY_COLOUR, DARK_GRAY_COLOUR)
    draw_border_lines(windowSurface, 425, 484, windowSurface.get_rect().centerx - 125, windowSurface.get_rect().centerx + 124,
                      LIGHT_GRAY_COLOUR, DARK_GRAY_COLOUR)
             
    # Draw big knight and bishop
    windowSurface.blit(bigbishop.image, bigbishop.rect)
    windowSurface.blit(bigknight.image, bigknight.rect)
       
    # Update screen
    pygame.display.update()


def process_menu(windowSurface):
    """Respond to keyboard and mouse clicks when on menu screen, return the value of option clicked"""

    # Continue in loop until option is chosen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()      
            elif event.type == MOUSEBUTTONUP:
                # Within the first option selection area (single player)
                if (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 215 and event.pos[1] <= 274):
                    #Run code for selecting difficulty
                    display_AI_options(windowSurface)
                    return process_AI_options()    
                # Within the second option selection area (two player)
                elif (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 285 and event.pos[1] <= 344):
                    return TWO_PLAYER
                # Within the third option selection area (how to play)
                elif (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 355 and event.pos[1] <= 414):
                    return HOW_TO_PLAY
                # Within the fourth option selection area (exit)
                elif (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 425 and event.pos[1] <= 484):
                    return EXIT


def display_AI_options(windowSurface):
    """Display the screen for when player is selecting AI difficulty"""

    # Set up font
    basicFont = pygame.font.SysFont("Arial", 40)

    # Draw rectangles to be clicked on                                     
    pygame.draw.rect(windowSurface, MENU_BEIGE_COLOUR, (windowSurface.get_rect().centerx - 125, 285, 250, 60))
    pygame.draw.rect(windowSurface, MENU_BEIGE_COLOUR, (windowSurface.get_rect().centerx - 125, 355, 250, 60))                                      
    pygame.draw.rect(windowSurface, MENU_BEIGE_COLOUR, (windowSurface.get_rect().centerx - 125, 425, 250, 60))
    
    # Draw options to click on
    draw_text_middle("Easy", basicFont, windowSurface, windowSurface.get_rect().centerx, 290, BLACK_COLOUR)
    draw_text_middle("Medium", basicFont, windowSurface, windowSurface.get_rect().centerx, 360, BLACK_COLOUR)
    draw_text_middle("Hard", basicFont, windowSurface, windowSurface.get_rect().centerx, 430, BLACK_COLOUR)

    # Draw lines around rectangles for 3d effect
    draw_border_lines(windowSurface, 285, 344, windowSurface.get_rect().centerx - 125,
                      windowSurface.get_rect().centerx + 124, LIGHT_BEIGE_COLOUR, DARK_BEIGE_COLOUR)
    draw_border_lines(windowSurface, 355, 414, windowSurface.get_rect().centerx - 125,
                      windowSurface.get_rect().centerx + 124, LIGHT_BEIGE_COLOUR, DARK_BEIGE_COLOUR)
    draw_border_lines(windowSurface, 425, 484, windowSurface.get_rect().centerx - 125,
                      windowSurface.get_rect().centerx + 124, LIGHT_BEIGE_COLOUR, DARK_BEIGE_COLOUR)     
                    
    # Update screen
    pygame.display.update()


def process_AI_options():
    """Respond to keyboard and mouse clicks when on AI level screen, return the value of option clicked"""

    # Continue in loop until option is chosen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
                # Within the first option selection area (back to main menu (don't show single player difficulties)
                if (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 215 and event.pos[1] <= 274):
                    return DESELECT_SINGLE_PLAYER
                # Within the second option selection area (easy difficulty)
                elif (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 285 and event.pos[1] <= 344):
                    return AI_EASY
                # Within the third option selection area (medium difficulty)
                elif (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 355 and event.pos[1] <= 414):
                    return AI_MEDIUM
                # Within the fourth option selection area (hard difficulty)
                elif (event.pos[0] >= 375 and event.pos[0] <= 625 and
                    event.pos[1] >= 425 and event.pos[1] <= 484):
                    return AI_HARD


def run_main_menu(windowSurface, bigbishop, bigknight, homeicon, hinticon, soundicon, menuhomeicon):
    """Run the main menu"""

    while True:
        # Display and process the home menu
        display_menu(windowSurface, bigbishop, bigknight)
        chosen = process_menu(windowSurface)
        
        # Return/initiate code for selected option
        if chosen == AI_EASY:
            return Game(True, EASY)     #Run game on easy (AI)
        elif chosen == AI_MEDIUM:
            return Game(True, MEDIUM)   #Run game on medium (AI)
        elif chosen == AI_HARD:
            return Game(True, HARD)     #Run game on hard (AI)
        elif chosen == TWO_PLAYER:
            return Game(False, -1)      #Run game (two player)
        elif chosen == HOW_TO_PLAY:
            # Run code for instructions screen
            display_instructions(windowSurface, homeicon, hinticon, soundicon, menuhomeicon)
            process_instructions()   
        elif chosen == EXIT:
            terminate()


def process_win_screen():
    """Respond to keyboard and mouse clicks when on game over screen"""
    
    # Continue in loop until option is chosen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
                # Within the "DONE" selection area
                if (event.pos[0] >= 290 and event.pos[0] <= 410 and
                    event.pos[1] >= 353 and event.pos[1] <= 387):
                    return
    

class Surfaceboard(pygame.sprite.Sprite):
    """The actual chess board image"""
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(image, (600, 600))
        self.rect = self.image.get_rect()
        self.rect.top = 50
        self.rect.left = 50


class BigBishopImage(pygame.sprite.Sprite):
    """Image of bishop for menu screen"""
    def __init__(self, image, left, ymiddle):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(image, (300, 300))
        self.rect = self.image.get_rect()
        self.rect.centery = ymiddle - 2
        self.rect.left = left


class BigKnightImage(pygame.sprite.Sprite):
    """Image of knight for menu screen"""
    def __init__(self, image, left, ymiddle):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(image, (300, 300))
        self.rect = self.image.get_rect()
        self.rect.centery = ymiddle
        self.rect.left = left


class HomeIcon(pygame.sprite.Sprite):
    """The home button image"""
    def __init__(self, image, top, left):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(image, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left


class SoundIcon(pygame.sprite.Sprite):
    """The sound button image"""
    def __init__(self, image, top, left):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(image, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left


class HintIcon(pygame.sprite.Sprite):
    """The hint button image"""
    def __init__(self, image, top, left):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.transform.scale(image, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left


class RecentMove:
    """The most recent move of a team/colour"""
    def __init__(self, initial, final, kind):
        self.initial = initial    # Starting position (from)
        self.final = final        # Ending point (to)
        self.kind = kind          # Type of piece moved


class Piece(pygame.sprite.Sprite):
    """A piece on the board"""
    def __init__(self, image, colour, kind, points):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(image, (65, 65))   # Image for piece
        self.rect = self.image.get_rect()                      # Rectangle of iamge
        self.colour = colour                                   # Colour of piece
        self.kind = kind                                       # Type of piece
        self.points = points                                   # Point value of piece


class ChessAI():
    """The logic/algorithm used for the AI"""

    def get_best_move(self, board, colour, depth, beta, alpha):
        """Returns score, initial slot, and final slot of best possible move with inputted colour and depth"""

        # End of recursion/reached max depth
        if depth == 0:
            
            # Check for stalemate at this position
            if not board.is_in_check(opposite_colour(colour)):
                if board.get_out_check(opposite_colour(colour)) == 0:
                    return (0, (-1, -1), (-1, -1))

            # Return the score of the board at this depth
            return (board.get_board_score(colour), (-1, -1), (-1, -1))

        # Colour is white, maximize possible score
        if colour == WHITE:
            best_score = -10000

            # Generate all moves for colour with current board
            each_possible_move = self.generate_all_moves(board, colour) 

            # Make each possible move
            for move in each_possible_move:
                new_board = board.make_copy()
                new_board.make_move(move[0], move[1], None)
                new_board.does_pawn_promote(move[1][0], move[1][1])

                # Generate score of move
                score = (self.get_best_move(new_board, opposite_colour(colour), depth - 1, beta, alpha))[0]

                # Update best score and best move
                if score > best_score:
                    best_score = score
                    best_move = move

                # Handle alpha & beta (optimization)
                if best_score >= beta:
                    break
                if best_score > alpha:
                    alpha = best_score

        # Colour is black, minimize possible score    
        else:
            best_score = 10000

            # Generate all moves for colour with current board
            each_possible_move = self.generate_all_moves(board, colour)
            
            # Make each possible move
            for move in each_possible_move:
                new_board = board.make_copy()
                new_board.make_move(move[0], move[1], None)
                new_board.does_pawn_promote(move[1][0], move[1][1])

                # Generate score of move
                score = (self.get_best_move(new_board, opposite_colour(colour), depth - 1, beta, alpha))[0]

                # Update best score and best move
                if score < best_score:
                    best_score = score
                    best_move = move

                # Handle alpha & beta (optimization)
                if best_score <= alpha:
                    break
                if best_score < beta:
                    beta = best_score


        #If no moves possible from given board
        if best_score == 10000 or best_score == -10000:

            if not board.is_in_check(opposite_colour(colour)):
                if board.get_out_check(opposite_colour(colour)) == 0:
                    return (0, (-1, -1), (-1, -1))

            result = (board.get_board_score(colour,), (-1, -1), (-1, -1))
            return result

        # Return the move with the best score
        return (best_score, best_move[0], best_move[1])
                    

    def generate_all_moves(self, board, colour):
        """Generate and return all possible moves of inputted colour"""

        moves = []

        # Colour is white, start in top left to optimize move generation time (alpha/beta related)
        if colour == WHITE:
            start = 0
            end = 8
            step = 1   
        # Colour is black, start in bottom left to optimize move generation time (alpha/beta related)
        else:
            start = 7
            end = -1
            step = -1
        
        # Go through each slot in board
        for row in range(start, end, step):
            for col in range(SIZE):
                # Check conditions
                if board.board[row][col] != None and board.board[row][col].colour == colour:
                    # Generate all possible moves from chosen piece
                    current = board.valid_moves(row, col)
                    # Remove moves that result in check
                    current = board.do_not_move_into_check(current, (row, col), opposite_colour(colour))
                    
                    # Append starting and ending position of each valid move to final move list
                    for i in range(len(current)):
                        moves.append(((row,col), current[i]))

        # If there are any moves, go to sorting function
        if len(moves) > 0:
            moves = self.rank_moves(board, moves)

        return moves


    def rank_moves(self, board, moves):
        """Sorts moves into order of how likely they are to be made/how extreme
        they are, optimizes alpha beta and time taken for AI to select a move"""

        scored_moves = []
        # Assign values to each move (do they capture a piece, and what piece they captured
        for move in moves:
            score = 0
            if board.board[move[1][0]][move[1][1]] != None: 
                score += board.board[move[1][0]][move[1][1]].points

            move = move + (score,)     # Add score to tuple
            scored_moves.append(move)  # Add tuple to new list

        # Sort moves by score then reverse (higher scores processed first when AI chooses move)
        sorted_moves = sorted(scored_moves, key=lambda new: new[2])
        sorted_moves.reverse()

        # Randomize moves that result in the same score 
        final_list = []
        value = sorted_moves[0][2]   # The score of the current piece in list
        temp_list = []               # Temperary list of all moves with same current score (value)

        # Go though each move
        for x in range(len(sorted_moves)):
            # If moved on to lower score section
            if sorted_moves[x][2] != value:

                # Shuffle the moves from temperary list and add it to final list
                random.shuffle(temp_list)
                final_list.extend(temp_list)

                # Reset values with next score (ex 9 to 7)
                value = sorted_moves[x][2]
                temp_list = [sorted_moves[x]]

            # Append this move to temperary list of same scores
            else:
                temp_list.append(sorted_moves[x])

        # Shuffle and add moves of last score in list (9, 8, 5, 2, 0 (shuffle 0 score moves))
        random.shuffle(temp_list)
        final_list.extend(temp_list) 
                
        # Return the sorted list
        return final_list


class Board():
    """The board and it's logic"""
    def __init__(self, pieces):

        self.pieces = pieces                                       # A list of the different pieces
        self.board = create_2D_array(8, 8, None)                   # Create the board
        self.moved = create_2D_array(8, 8, False)                  # Create array that keeps track of what pieces have moved
        self.recentblack = RecentMove((-1,-1), (-1,-1), None)      # Create most recent black move
        self.recentwhite = RecentMove((-1,-1), (-1,-1), None)      # Create most recent white move
        self.incheck = [False, False]                              # Assign both colours to not in check


    def set_up_initial_board(self):
        """Set up the pieces, assign them to standard starting locations"""

        # - BLACK -
        # Rooks
        self.board[0][0] = self.pieces[BLACK][ROOK]
        self.board[0][7] = self.pieces[BLACK][ROOK]
        # Knights
        self.board[0][1] = self.pieces[BLACK][KNIGHT]
        self.board[0][6] = self.pieces[BLACK][KNIGHT]
        # Bishops
        self.board[0][2] = self.pieces[BLACK][BISHOP]
        self.board[0][5] = self.pieces[BLACK][BISHOP]
        # Queen
        self.board[0][3] = self.pieces[BLACK][QUEEN]
        # King
        self.board[0][4] = self.pieces[BLACK][KING]
        # Pawns
        for col in range(SIZE):
            self.board[1][col] = self.pieces[BLACK][PAWN]

        # - WHITE - 
        # Rooks
        self.board[7][0] = self.pieces[WHITE][ROOK]
        self.board[7][7] = self.pieces[WHITE][ROOK]
        # Knights
        self.board[7][1] = self.pieces[WHITE][KNIGHT]
        self.board[7][6] = self.pieces[WHITE][KNIGHT]
        # Bishops
        self.board[7][2] = self.pieces[WHITE][BISHOP]
        self.board[7][5] = self.pieces[WHITE][BISHOP]
        # Queen
        self.board[7][3] = self.pieces[WHITE][QUEEN]
        # King
        self.board[7][4] = self.pieces[WHITE][KING]
        # Pawns
        for col in range(SIZE):
            self.board[6][col] = self.pieces[WHITE][PAWN]        


    def make_copy(self):
        """Make and return a copy of the board class instance"""

        # Make a new board class instance (copy)
        board_copy = Board(self.pieces)      

        # Make the board position carry oveer
        for row in range(SIZE):
            board_copy.board[row] = copy.copy(self.board[row])

        # Make the list of pieces that have moved carry over
        for row in range(len(self.moved)):
            board_copy.moved[row] = copy.copy(self.moved[row])
            
        return board_copy
    

    def does_collide(self, row, col, validmoves, colour):
        """Checks if possible moves collides with a piece or edge of board"""

        # Check if within board
        if row >= 0 and col >= 0 and row < 8 and col < 8:
            # Check if another piece in selected slot (collided with piece)
            if self.board[row][col] != None:
                # Check if colliding with piece of opposite team/colour, append that spot and stop checking
                if self.board[row][col].colour != colour:
                    validmoves.append((row, col))
                return True
            else:
                return False
        else:
            return True


    def pawn_capture(self, row, col, validmoves):
        """Checks if pawn can take a piece, if so, appends it to validmoves"""

        # Colour/team is black, pawns moving down
        if self.board[row][col].colour == BLACK:
            direction = 1
        # Colour/team is white, pawns moving up
        else:
            direction = -1

        # Pawn isn't on final row (can't move forward)
        if row > 0 and row < 7:
            
            # Check if pawn can capture right (exclude if already farthest right)
            if col >= 0 and col < 7:
                if self.board[row+direction][col+1] != None:
                    if self.board[row+direction][col+1].colour != self.board[row][col].colour:
                         validmoves.append((row+direction, col+1))

            # Check if pawn can capture left (exclude if already farthest left)
            if col > 0 and col < 8:
                    if self.board[row+direction][col-1] != None:
                        if self.board[row+direction][col-1].colour != self.board[row][col].colour:
                            validmoves.append((row+direction, col-1))


    def valid_moves(self, row, col):
        """Returns list of possible moves from selected piece"""
    
        validmoves = []

        # Rook
        if self.board[row][col].kind == ROOK:
            rook_directions = [(1,  0), (0,  1), (-1,  0), (0, -1)]         # Directions rook can travel

            # Iterate through each direction 
            for dir in rook_directions:
                pos = (row + dir[0], col + dir[1])
                # Check for colliding with other pieces or edge of board
                while not self.does_collide(pos[0], pos[1], validmoves, self.board[row][col].colour):
                    validmoves.append((pos[0], pos[1]))                     # Append move
                    pos = (pos[0] + dir[0], pos[1] + dir[1])                # Update position
                    
               
        # Knight
        elif self.board[row][col].kind == KNIGHT:
            validmoves.append((row-1,col-2))
            validmoves.append((row-2, col-1))
            validmoves.append((row-1, col+2))
            validmoves.append((row-2, col+1))
            validmoves.append((row+1, col-2))
            validmoves.append((row+2, col-1))
            validmoves.append((row+1, col+2))
            validmoves.append((row+2, col+1))


        # Bishop
        elif self.board[row][col].kind == BISHOP:
            bishop_directions = [(1,  1), (-1,  -1), (-1,  1), (1, -1)]     #Directions bishop can travel

            # Iterate through each direction
            for dir in bishop_directions:
                pos = (row + dir[0], col + dir[1])
                # Check for colliding with other pieces or edge of board
                while not self.does_collide(pos[0], pos[1], validmoves, self.board[row][col].colour):
                    validmoves.append((pos[0], pos[1]))                     # Append move
                    pos = (pos[0] + dir[0], pos[1] + dir[1])                # Update position


        # Queen
        elif self.board[row][col].kind == QUEEN:
            #Directions queen can travel
            queen_directions = [(1,  1), (-1,  -1), (-1,  1), (1, -1), (1,  0), (0,  1), (-1,  0), (0, -1)]

            # Iterate through each direction
            for dir in queen_directions:
                pos = (row + dir[0], col + dir[1])
                # Check for colliding with other pieces or edge of board
                while not self.does_collide(pos[0], pos[1], validmoves, self.board[row][col].colour):
                    validmoves.append((pos[0], pos[1]))                 # Append move
                    pos = (pos[0] + dir[0], pos[1] + dir[1])            # Update position


        # King
        elif self.board[row][col].kind == KING:
            validmoves.append((row-1, col-1))
            validmoves.append((row-1, col))
            validmoves.append((row-1, col+1))
            validmoves.append((row,   col-1))
            validmoves.append((row,   col+1))
            validmoves.append((row+1, col-1))
            validmoves.append((row+1, col))
            validmoves.append((row+1, col+1))

            # CASTLING
            # Check castling conditions
            colour = opposite_colour(self.board[row][col].colour)
            incheck = self.incheck[self.board[row][col].colour]
            if not self.moved[row][col] and not incheck:
        
                # Castle long (left)
                if self.board[row][0] != None:
                    #  Check conditions
                    if self.moved[row][0] == False and self.board[row][0].kind == ROOK:
                        if self.board[row][1] == None and self.board[row][2] == None and self.board[row][3] == None:
                            # Check if moving through check (condition)
                            path = ((row, 3), (row, 2))
                            path = self.do_not_move_into_check(path, (row, col), colour)
                            if len(path) == 2:
                                validmoves.append((row, 2))

                # Castle short (right)
                if self.board[row][7] != None:
                    # Check conditions
                    if self.moved[row][7] == False and self.board[row][7].kind == ROOK:
                        if self.board[row][5] == None and self.board[row][6] == None:
                            # Check if moving through check (condition)
                            path = ((row, 5), (row, 6))
                            path = self.do_not_move_into_check(path, (row, col), colour)
                            if len(path) == 2:
                                validmoves.append((row, 6))

        # Pawn
        elif self.board[row][col].kind == PAWN:

            # Pawn is black, moving down
            if self.board[row][col].colour == BLACK:

                # Check move 2 squares  
                if row == 1:
                    if self.board[row+2][col] == None and self.board[row+1][col] == None:
                        validmoves.append((row+2, col))
                # Check move 1 square 
                if row < 7 and self.board[row+1][col] == None:
                    validmoves.append((row+1, col))
                    
                # En Passant
                if row == 4:
                    # Is recent other team move pawn double move
                    if self.recentwhite.kind == PAWN:
                        if self.recentwhite.initial[0] - 2 == self.recentwhite.final[0]:
                            # Check if other team recent pawn move is to the left of your pawn
                            if self.recentwhite.initial[1] - col == - 1:
                                validmoves.append((row+1, col-1))
                            # Check if other team recent pawn move is to the right of your pawn 
                            elif self.recentwhite.initial[1] - col == 1:
                                validmoves.append((row+1, col+1))


            # Pawn is white, moving up
            else:

                #C heck move 2 squares
                if row == 6:
                    if self.board[row-2][col] == None and self.board[row-1][col] == None:
                        validmoves.append((row-2, col))
                # Check move 1 square
                if row > 0 and self.board[row-1][col] == None:
                    validmoves.append((row-1, col))
                    
                # En Passant
                if row == 3:
                    # Is recent other team move pawn double move
                    if self.recentblack.kind == PAWN:
                        if self.recentblack.initial[0] + 2 == self.recentblack.final[0]:
                            # Check if other team recent pawn move is to the left of your pawn
                            if col - self.recentblack.initial[1] == 1:
                                validmoves.append((row-1, col-1))
                            # Check if other team recent pawn move is to the right of your pawn
                            elif col - self.recentblack.initial[1] == -1:
                                validmoves.append((row-1, col+1))

            # Checks if pawn can capture a piece
            self.pawn_capture(row, col, validmoves)
            
        # If knight or king is selected
        if self.board[row][col].kind == KING or self.board[row][col].kind == KNIGHT:
            # Remove valid moves that move to a spot with same team (for knight and king)
            for r in range(len(self.board)):
                for c in range(len(self.board)):
                    if self.board[r][c] != None:
                        if self.board[r][c].colour == self.board[row][col].colour:
                            check = (r, c)
                            if check in validmoves:
                                validmoves.remove(check)
                                
            # Remove valid moves from outside the board (for knight and king)
            new = []
            for i in range(len(validmoves)):
                if ((validmoves[i])[0] >= 0 and (validmoves[i])[0] <= 7 and
                    (validmoves[i])[1] >= 0 and (validmoves[i])[1] <= 7):
                    new.append(validmoves[i])
            validmoves = new
            

        # Return calculated moves
        return validmoves


    def make_move(self, firstslot, secondslot, graveyard):
        """Makes move using inputted starting and ending slots/squares, handles captures"""

        # Update most recent move
        if self.board[firstslot[0]][firstslot[1]].colour == WHITE:
            self.recentwhite = RecentMove(firstslot, secondslot, self.board[firstslot[0]][firstslot[1]].kind)
        else:
            self.recentblack = RecentMove(firstslot, secondslot, self.board[firstslot[0]][firstslot[1]].kind)

        # En passant right, handle non-normal capture
        if (self.board[firstslot[0]][firstslot[1]].kind == PAWN and firstslot[1] - secondslot[1] == -1
        and self.board[secondslot[0]][secondslot[1]] == None):
            if graveyard != None:
                graveyard[self.board[firstslot[0]][firstslot[1]+1].colour].append(self.board[firstslot[0]][firstslot[1]+1])
            self.board[firstslot[0]][firstslot[1]+1] = None

        # En passant left, handle non-normal capture
        elif (self.board[firstslot[0]][firstslot[1]].kind == PAWN and firstslot[1] - secondslot[1] == 1
        and self.board[secondslot[0]][secondslot[1]] == None):
            if graveyard != None:
                graveyard[self.board[firstslot[0]][firstslot[1]-1].colour].append(self.board[firstslot[0]][firstslot[1]-1])
            self.board[firstslot[0]][firstslot[1]-1] = None

        # Check if selected move is castling to left, move rook accordingly
        elif self.board[firstslot[0]][firstslot[1]].kind == KING and firstslot[1] - secondslot[1] == 2:
            self.moved[firstslot[0]][0] = True
            self.board[firstslot[0]][3] = self.board[firstslot[0]][0]
            self.board[firstslot[0]][0] = None

        # Check if selected move is castling to right, move rook accordingly
        elif self.board[firstslot[0]][firstslot[1]].kind == KING and firstslot[1] - secondslot[1] == -2:
            self.moved[firstslot[0]][7] = True
            self.board[firstslot[0]][5] = self.board[firstslot[0]][7]
            self.board[firstslot[0]][7] = None
            
        # Check if piece has been captured, append to graveyard
        if self.board[secondslot[0]][secondslot[1]] != None:
            if graveyard != None:
                graveyard[self.board[secondslot[0]][secondslot[1]].colour].append(self.board[secondslot[0]][secondslot[1]])

        # Update position of piece moved
        self.board[secondslot[0]][secondslot[1]] = self.board[firstslot[0]][firstslot[1]]
        self.board[firstslot[0]][firstslot[1]] = None

        # Update that piece has moved (needed for castling)
        self.moved[firstslot[0]][firstslot[1]] = True


    def is_in_check(self, colour):
        """Checks if king of opposite colour is in check"""

        # Creates all possible moves for the entered colour
        moves = self.create_all_moves(colour)

        # Go through each spot on board
        for row in range(SIZE):
            for col in range(SIZE):
                if self.board[row][col] != None:
                    # Check if piece is king of opposite colour
                    if self.board[row][col].kind == KING and self.board[row][col].colour != colour:
                        # If this square is a possible move of other team, this king is in check
                        if (row, col) in moves:
                            return True
        return False


    def create_all_moves(self, colour):
        """Generates all possible moves of inputted colour"""

        moves = []
        # Go through each slot/square on board
        for row in range(SIZE):
            for col in range(SIZE):
                # Check conditions
                if self.board[row][col] != None and self.board[row][col].colour == colour:
                        # Generate moves of selected piece, append moves to all moves list
                        current = (self.valid_moves(row, col))
                        for i in range(len(current)):
                            moves.append(current[i])
        return moves


    def do_not_move_into_check(self, validmoves, firstslot, colour):
        """Returns moves from "valid moves" that don't move into check"""

        final = []
        # Go through list of "valid moves"
        for i in range(len(validmoves)):

            # Make copy of board and make each move, check that move doesn't move into check
            copy = self.make_copy()
            copy.make_move(firstslot, validmoves[i], None)

            # If move doesn't move into check, append it to final list
            if not copy.is_in_check(colour):
                final.append(validmoves[i])

        return final


    def get_board_score(self, colour_to_move):
        """Gets the relative score of pieces on board, needed for AI. White adds points, black subtracts"""

        score = 0

        # Check if colour moving is in checkmate, if so make extreme score for this board/move
        if self.is_in_check(opposite_colour(colour_to_move)):   #If in check
            if self.get_out_check(opposite_colour(colour_to_move)) == 0:    #If don't have any moves (checkmate)
                if colour_to_move == WHITE:
                    return -1000
                else:
                    return 1000

        # Iterate through each slot/square on board
        for row in range(SIZE):
            for col in range(SIZE):
                if self.board[row][col] != None:
                    
                    # Piece is white, add points based on piece, add points for advancement on board (aggresive AI)
                    if self.board[row][col].colour == WHITE:
                        score += (self.board[row][col].points)*10
                        score += min(7 - row, 4)
                        # Advancement bonus. Only add points until row before pawns so no pointless sacrifices
                            
                    # Piece is black, subtract points based on piece, subtract points for advancement on board (aggresive AI)
                    elif self.board[row][col].colour == BLACK:
                        score -= (self.board[row][col].points)*10
                        score -= min(row, 4)
                        # Advancement bonus. Only add points until row before pawns so no pointless sacrifices

        return score
    

    def does_pawn_promote(self, row, col):
        """Checks if pawn is at end, autimatically promotes it to queen, needed for AI"""

        colour = self.board[row][col].colour
        # Check if piece is pawn and at other side of board
        if self.board[row][col].kind == PAWN:
            if (colour == BLACK and row == 7) or (colour == WHITE and row == 0):
                # Change piece to queen
                self.board[row][col] = self.pieces[colour][QUEEN]
    

    def get_out_check(self, colour_just_moved):
        """Returns if player has any valid moves or not"""
        
        # Go through each slot/sqaure on board, get moves of given colour
        for row in range(SIZE):
            for col in range(SIZE):
                # Check requirements
                if self.board[row][col] != None and self.board[row][col].colour != colour_just_moved:
                        # Make a list of moves from current piece, check that they don't move into check, add them to final moves
                        current = self.valid_moves(row, col)
                        for x in range(len(current)):
                            iteration = self.do_not_move_into_check([current[x]], (row, col), colour_just_moved)
                            if len(iteration) > 0:
                                return 1
        return 0


class Game():
    """Represents an instance of the game"""

    def __init__(self, AI, difficulty):
        """Constructor. Create all attributes and initialize the game"""

        self.game_over = False

        # Load the background board image in
        surfaceimage = load_image("board.png")
        self.surfaceboard = Surfaceboard(surfaceimage)

        # Load the home icon image in
        homeiconimage = load_image("home_icon.png")
        self.homeicon = HomeIcon(homeiconimage, 5, 960)
        
        # Load the sound icon image in
        soundiconimage = load_image("sound_icon.png")
        self.soundicon = SoundIcon(soundiconimage, 5, 920)

        # Load the no sound icon (mute) image in
        nosoundiconimage = load_image("mute_icon.png")
        self.nosoundicon = SoundIcon(nosoundiconimage, 5, 920)

        # Load the hint icon image in
        hintimage = load_image("lightbulb.png")
        self.hinticon = HintIcon(hintimage, 5, 877)

        # Create pieces list
        self.pieces = create_2D_array(2, 6, None)

        # Create graveyard list (captures)
        self.graveyard = create_2D_array(2, 1, None)


        # Load and create the pieces:
        # ---------------------------
        # BLACK
        brimage = load_image("black_rook.png")
        self.pieces[BLACK][ROOK] = Piece(brimage, BLACK, ROOK, 5)
        bkimage = load_image("black_knight.png")
        self.pieces[BLACK][KNIGHT] = Piece(bkimage, BLACK, KNIGHT, 3)
        bbimage = load_image("black_bishop.png")
        self.pieces[BLACK][BISHOP] = Piece(bbimage, BLACK, BISHOP, 3)
        bqimage = load_image("black_queen.png")
        self.pieces[BLACK][QUEEN] = Piece(bqimage, BLACK, QUEEN, 9)
        bgimage = load_image("black_king.png")
        self.pieces[BLACK][KING] = Piece(bgimage, BLACK, KING, 1000)
        bpimage = load_image("black_pawn.png")
        self.pieces[BLACK][PAWN] = Piece(bpimage, BLACK, PAWN, 1)

        # WHITE
        wrimage = load_image("white_rook.png")
        self.pieces[WHITE][ROOK] = Piece(wrimage, WHITE, ROOK, 5)
        wkimage = load_image("white_knight.png")
        self.pieces[WHITE][KNIGHT] = Piece(wkimage, WHITE, KNIGHT, 3)
        wbimage = load_image("white_bishop.png")
        self.pieces[WHITE][BISHOP] = Piece(wbimage, WHITE, BISHOP, 3)
        wqimage = load_image("white_queen.png")
        self.pieces[WHITE][QUEEN] = Piece(wqimage, WHITE, QUEEN, 9)
        wgimage = load_image("white_king.png")
        self.pieces[WHITE][KING] = Piece(wgimage, WHITE, KING, 1000)
        wpimage = load_image("white_pawn.png")
        self.pieces[WHITE][PAWN] = Piece(wpimage, WHITE, PAWN, 1)

        # Instantiate board with pieces
        self.board = Board(self.pieces)
        self.board.set_up_initial_board()
           
        # Create list containing pieces that pawn could turn into
        self.pawnimages = [[self.pieces[BLACK][ROOK], self.pieces[BLACK][KNIGHT],
                            self.pieces[BLACK][BISHOP], self.pieces[BLACK][QUEEN]],
                           [self.pieces[WHITE][ROOK], self.pieces[WHITE][KNIGHT],
                            self.pieces[WHITE][BISHOP], self.pieces[WHITE][QUEEN]]]

        
        self.AI = AI                  # If the AI is runnning or not (boolean)
        self.difficulty = difficulty  # The difficulty of the AI (how much depth for recursion)

        # Set up sound effects
        self.piecemovesound = pygame.mixer.Sound("chess_piece_move.mp3")
        self.soundeffects = True

        # Set hint, firstslot, and validmoves to unselected
        self.hint = ((-1, -1), (-1, -1))
        self.firstslot = (-1, -1)
        self.validmoves = []

        # Set up scores of each team
        self.whitescore = 0
        self.blackscore = 0

        # Set up booleans for if game won or tied
        self.win = [False, False]
        self.tie = False

        # White always goes first
        self.turn = WHITE  

        # If the home button has been clicked
        self.home_button = False    


    def process_events(self, windowSurface):
        """Respond to keyboard and mouse clicks within the game"""

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()            
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:

                # Home button clicked on
                if (event.pos[0] >= 960 and event.pos[0] < 995
                and event.pos[1] >= 5 and event.pos[1] < 40):
                    # Return to main menu
                    self.home_button = True

                # Sound button clicked on
                elif (event.pos[0] >= 920 and event.pos[0] < 955
                and event.pos[1] >= 5 and event.pos[1] < 40):
                    # Turn on/off sound effects
                    if self.soundeffects:
                        self.soundeffects = False
                    else:
                        self.soundeffects = True

                # Hint button clicked on
                elif (event.pos[0] >= 877 and event.pos[0] < 912
                and event.pos[1] >= 5 and event.pos[1] < 40):
                    # De-select hint
                    if self.hint != ((-1, -1), (-1, -1)):
                        self.hint = ((-1, -1), (-1, -1))
                    # Run AI for the hint, update self.hint with best move, to and from of piece
                    else:
                        ai = ChessAI()
                        stats = ai.get_best_move(self.board, self.turn, HARD, 1000, -1000)
                        self.hint = (stats[1], stats[2])

                # Within the actual chess board
                elif (event.pos[0] >= 50 and event.pos[0] < 650 and
                    event.pos[1] >= 50 and event.pos[1] < 650):

                    # If first click has not been made (haven't selected a piece yet)
                    if self.firstslot == (-1, -1):

                        # Get the slot of the piece selected (transfer co-ordinates to slot in array)
                        slot = self.get_slot((event.pos[0], event.pos[1]))

                        # Nothing happens if user clicks a blank spot (not a piece) or clicks on the other team
                        if (self.board.board[slot[0]][slot[1]] != None
                        and self.board.board[slot[0]][slot[1]].colour == self.turn):
                            
                            # Generate valid moves of selected piece
                            self.validmoves = self.board.valid_moves(slot[0], slot[1])

                            # Get rid of moves that move into check
                            self.validmoves = self.board.do_not_move_into_check(self.validmoves, slot,
                                                                                opposite_colour(self.board.board[slot[0]][slot[1]].colour))
                                           
                            # If no valid moves, don't let them select this piece
                            if len(self.validmoves) > 0:
                                self.firstslot = slot

                    # Lets the player can de-select a piece
                    elif self.get_slot((event.pos[0], event.pos[1])) == self.firstslot:
                        self.firstslot = (-1, -1)
                        self.validmoves = []
                            
                    # A piece has been selected, process where they want to move the piece
                    else:
                        
                        # Get the slot of the piece selected (transfer co-ordinates to slot in array)
                        secondslot = self.get_slot((event.pos[0], event.pos[1]))

                        # If the spot they clicked on is a valid move
                        if secondslot in self.validmoves:

                            # Make the move
                            self.board.make_move(self.firstslot, secondslot, self.graveyard)

                            # If sound effects on, play sound effect for moving a piece
                            if self.soundeffects:
                                self.piecemovesound.play()

                            # Reset variables 
                            self.hint = ((-1, -1), (-1, -1))
                            self.firstslot = (-1, -1)
                            self.validmoves = []

                            # Check if pawns have reached other side (for players, not AI)
                            if self.turn == BLACK and not self.AI:
                                self.display_frame(windowSurface)
                                self.check_if_pawns_at_end(windowSurface, 7, BLACK)
                            else:
                                self.display_frame(windowSurface)
                                self.check_if_pawns_at_end(windowSurface, 0, WHITE)

                            # Update game conditions
                            self.update_check_conditions()
                            # Switch the turn
                            self.turn = opposite_colour(self.turn)

                         
    def display_frame(self, windowSurface):
        """Update the screen of main game"""
        
        # Draw tan background onto the surface
        windowSurface.fill(TAN_COLOUR)
        
        # Draw outline of board (rectangle (square) under board)
        pygame.draw.rect(windowSurface, BLACK_COLOUR, (self.surfaceboard.rect.left-5,
                                                      self.surfaceboard.rect.top-5,
                                                      self.surfaceboard.rect.width+10,
                                                      self.surfaceboard.rect.height+10))
        # Draw white squares on board (rectangle (square) under transparent board)
        pygame.draw.rect(windowSurface, WHITE_COLOUR, (self.surfaceboard.rect.left,
                                                      self.surfaceboard.rect.top,
                                                      self.surfaceboard.rect.width,
                                                      self.surfaceboard.rect.height))

        # Display the chess board image
        windowSurface.blit(self.surfaceboard.image, self.surfaceboard.rect)

        # Display the home icon
        windowSurface.blit(self.homeicon.image, self.homeicon.rect)

        # Display the sound icon, either normal or mute depending on if it's toggled on or off
        if self.soundeffects:
            windowSurface.blit(self.soundicon.image, self.soundicon.rect)
        else:
            windowSurface.blit(self.nosoundicon.image, self.nosoundicon.rect)

        # Display the hint icon
        windowSurface.blit(self.hinticon.image, self.hinticon.rect)

        # Set up fonts
        basicFont = pygame.font.SysFont("Arial", 30)
        winFont = pygame.font.SysFont("Arial", 37)
        doneFont = pygame.font.SysFont("Arial", 20)

        # Display the scores
        scoretext = ["Black Score: " + str(self.blackscore), "White Score: " + str(self.whitescore)]
        scoreheight = [5, 660]
        for i in range(len(scoretext)):
            draw_text(scoretext[i], basicFont, windowSurface, 45, scoreheight[i], BLACK_COLOUR)

        # Display the captured captions
        capturedtextheight = [45, 350]
        for i in range(len(capturedtextheight)):
            draw_text("Captured:", basicFont, windowSurface, 675, capturedtextheight[i], BLACK_COLOUR)

        # Display the captured pieces:
        capturedheights = [385, 80]                     #Seperate heights for black and white
        # Go through the graveyard array, display pieces stored in it
        for row in range(len(self.graveyard)):
            height = capturedheights[row]
            left = 665
            counter = 5
            for col in range(len(self.graveyard[row])):
                if self.graveyard[row][col] != None:    #When array is created it only holds None, no pieces captured yet

                    # Update position of piece to be displayed, display the piece
                    self.graveyard[row][col].rect.left = left
                    self.graveyard[row][col].rect.top = height
                    windowSurface.blit(self.graveyard[row][col].image, self.graveyard[row][col].rect)
                    
                    # Decrease counter and move ticker to right
                    counter -= 1
                    left += 65
                    
                    # If 5 pieces displayed in given row, go to next row, reset/change variables
                    if counter == 0:    
                        height += 65
                        left = 665
                        counter = 5

        # Draw box around hint (from and to)
        if self.hint != ((-1, -1), (-1, -1)):

            # Hint Destination:
            # Corners of selected square 
            left = 51 + self.hint[1][1]*(600/8)
            right = left + (600/8) - 3
            top = 51 + self.hint[1][0]*(600/8)
            bottom = top + (600/8) - 4

            # Needed for display purposes (clean right side of board)
            if self.hint[1][1] == 7:
                right -= 1
            
            # Draw lines for box
            self.draw_box_around_piece(windowSurface, left, right, top, bottom, RED_COLOUR)

            # Hint Start:
            # Corners of selected squares
            left = 51 + self.hint[0][1]*(600/8)
            right = left + (600/8) - 3
            top = 51 + self.hint[0][0]*(600/8)
            bottom = top + (600/8) - 4

            # Needed for display purposes (clean right side of board)
            if self.hint[0][1] == 7:
                right -= 1
                    
            # Draw lines for box
            self.draw_box_around_piece(windowSurface, left, right, top, bottom, RED_COLOUR)

        # Draw a box around selected piece
        if self.firstslot != (-1, -1):
            
            # Corners of selected squares
            left = 51 + self.firstslot[1]*(600/8)
            right = left + (600/8) - 3
            top = 51 + self.firstslot[0]*(600/8)
            bottom = top + (600/8) - 4
            
            # Needed for display purposes (clean right side of board)
            if self.firstslot[1] == 7:
                right -= 1
                
            # Needed for display purposes (if hint is next to selected piece, has to do with chess board image)
            if self.hint != ((-1, -1), (-1, -1)):
                neighbour = self.check_neighbour_square()
                if neighbour == ON_RIGHT:
                    right -= 1
                elif neighbour == ON_LEFT:
                    left += 1
                    
            # Draw lines for box
            self.draw_box_around_piece(windowSurface, left, right, top, bottom, LIME_COLOUR)


        # Display possible moves for selected piece, iterate through board and check if the square is in valid moves
        for row in range(SIZE):
            for col in range(SIZE):
                
                # Check if this square is a valid move for piece selected
                slot = (row, col)
                if slot in self.validmoves:
                    
                    # Display green circle for given circle
                    width = 88 + col*(600/8)            #Find the x co-ordinate based off the column on board
                    height = 88.75 + row*(600/8)        #Find the y co-ordinate based off the row on board
                    gfxdraw.aacircle(windowSurface, int(width), int(height), 23, LIME_COLOUR)
                    gfxdraw.filled_circle(windowSurface, int(width), int(height), 23, LIME_COLOUR)

        # Display pieces on board, iterate thorugh each square/slot on board
        for row in range(SIZE):
            for col in range(SIZE):
                if self.board.board[row][col] != None:
                    self.board.board[row][col].rect.left = 55 + col*(600/8)
                    self.board.board[row][col].rect.top = 55 + row*(600/8)
                    windowSurface.blit(self.board.board[row][col].image, self.board.board[row][col].rect)

        # Display whose turn it is
        if not self.game_over:
            # Blacks turn
            if self.turn == BLACK:
                pygame.draw.rect(windowSurface, GREEN_COLOUR, (8, 73, 29, 29))
                pygame.draw.rect(windowSurface, BLACK_COLOUR, (11, 76, 23, 23))
            # Whites turn                                    
            else:
                pygame.draw.rect(windowSurface, GREEN_COLOUR, (8, 598, 29, 29))
                pygame.draw.rect(windowSurface, WHITE_TURN_COLOUR, (11, 601, 23, 23))
            
        # Display if black is in check
        if self.board.incheck[BLACK] and not self.win[WHITE]:
            draw_text("Black In Check", basicFont, windowSurface, 452, 5, BLACK_COLOUR)

        # Display if white is in check
        elif self.board.incheck[WHITE] and not self.win[BLACK]:
            draw_text("White In Check", basicFont, windowSurface, 451, 660, BLACK_COLOUR)

        # Display the win or tie screen if that has occurred
        if self.win[BLACK]:
            self.draw_win_or_tie_box(windowSurface, "Black Wins", winFont, doneFont, 259)
        elif self.win[WHITE]:
            self.draw_win_or_tie_box(windowSurface, "White Wins", winFont, doneFont, 257)
        elif self.tie:
            self.draw_win_or_tie_box(windowSurface, "Stalemate", winFont, doneFont, 265)
          
        # Update the screen
        pygame.display.update()


    def check_neighbour_square(self):
        """Determines if selected piece is next to hint display, and which side"""
        # Needed for display purposes because of background board image

        hintstart = self.hint[1]
        hintfinal = self.hint[0]

        if self.firstslot[0] == hintstart[0]:
            if self.firstslot[1] - 1 == hintstart[1]:
                return ON_LEFT
            elif self.firstslot[1] + 1 == hintstart[1]:
                return ON_RIGHT

        if self.firstslot[0] == hintfinal[0]:
            if self.firstslot[1] - 1 == hintfinal[1]:
                return ON_LEFT
            elif self.firstslot[1] + 1 == hintfinal[1]:
                return ON_RIGHT

        return NO_NEIGHBOUR

    
    def draw_win_or_tie_box(self, windowSurface, words, winFont, doneFont, left):
        """Draw the box for if a team has won or stalemate occured"""

        # Draw rectangle and inputted message (win/tie)
        pygame.draw.rect(windowSurface, BLACK_COLOUR, (245, 290, 210, 117))
        pygame.draw.rect(windowSurface, GRAY_COLOUR, (250, 295, 200, 107))
        draw_text(words, winFont, windowSurface, left, 305, BLACK_COLOUR)

        # Draw "DONE" button
        pygame.draw.rect(windowSurface, MENU_GRAY_COLOUR, (290, 353, 120, 35))
        draw_text_middle("CONTINUE", doneFont, windowSurface, 350, 358, BLACK_COLOUR)           
        draw_border_lines(windowSurface, 353, 387, 290, 410,
                          LIGHT_GRAY_COLOUR, DARK_GRAY_COLOUR)


    def draw_box_around_piece(self, windowSurface, left, right, top, bottom, colour):
        """Draws lines to create a box around a piece"""
        
        pygame.draw.line(windowSurface, colour, (left-1, top), (right+2, top), 4)        # Top
        pygame.draw.line(windowSurface, colour, (left-1, bottom), (right+2, bottom), 4)  # Bottom
        pygame.draw.line(windowSurface, colour, (left, top), (left, bottom), 4)          # Left
        pygame.draw.line(windowSurface, colour, (right, top), (right, bottom), 4)        # Right
        
        
    def get_slot(self, location):
        """Transfer the mouse click co-ordinates into a slot on the board/array"""

        squarelength = int(600/8)                    # The length of one square on the board
        row = int((location[1] - 50)/squarelength)   # Selected row
        col = int((location[0] - 50)/squarelength)   # Selected column

        return (row, col)


    def get_score(self, colour):
        """For normal game, score of taken pieces (in graveyard)"""

        score = 0     
        for col in range(len(self.graveyard[colour])):
            if self.graveyard[colour][col] != None:
                score += self.graveyard[colour][col].points
             
        return score
            

    def display_pawn_options(self, colour, pawnimages, windowSurface):
        """When a pawn is to be promoted, display the pieces to choose from"""

        # Display background border
        pygame.draw.rect(windowSurface, BLACK_COLOUR, (195, 300, 310, 100))
        # Display backgroudn
        pygame.draw.rect(windowSurface, GRAY_COLOUR, (200, 305, 300, 90))

        # Display the pieces to choose from (rook, knight, bishop, queen)
        top = 317
        left = 205
        for col in range(len(pawnimages[colour])):
            pawnimages[colour][col].rect.top = top
            pawnimages[colour][col].rect.left = left
            windowSurface.blit(pawnimages[colour][col].image, pawnimages[colour][col].rect)
            left += 75      # Move left parameter over (so the images are displayed beside each other)

        # Update screen
        pygame.display.update()

    
    def process_pawn_options(self):
        """Respond to keyboard and mouse clicks when the user is picking piece for pawn promotion"""

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminate()
                elif event.type == MOUSEBUTTONUP:
                    # Within the actual selection area
                    if (event.pos[0] >= 200 and event.pos[0] < 500
                    and event.pos[1] >= 275 and event.pos[1] < 425):
                        # Rook
                        if event.pos[0] < 275:
                            return 0
                        # Knight
                        elif event.pos[0] < 350:
                            return 1
                        # Bishop
                        elif event.pos[0] < 425:
                            return 2
                        # Queen
                        else:
                            return 3


    def check_if_pawns_at_end(self, windowSurface, side, colour):
        """Check if pawns have reached other side of board"""

        row = side
        # Check final row of inputted colour equivelent
        for c in range(SIZE):
            if self.board.board[row][c] != None:
                # If it detects a pawn at the other side, proceed to pawn promotion menu
                if self.board.board[row][c].kind == PAWN:
                    self.display_pawn_options(colour, self.pawnimages, windowSurface)

                    col = c
                    # Pawn promotion menu
                    spot = self.process_pawn_options()
                    self.board.board[row][col] = self.pawnimages[self.board.board[row][col].colour][spot]
                

    def update_check_conditions(self):
        """Update if players are in check, if the game has been won, or if the game has reached a tie (stalemate)"""

        # Reset conditions
        self.board.incheck = [False, False]
        self.win = [False, False]
        self.tie = False

        # Check if other player is in check and if player has won (turn dependent)
        if self.board.is_in_check(self.turn):
            self.board.incheck[opposite_colour(self.turn)] = True

            # Check if the game has been won (the other team has no moves and is in check
            if self.board.get_out_check(self.turn) == 0:
                self.win[self.turn] = True
                self.game_over = True

        # Tie/stalemate
        else:
            # Check if other player has no legal moves, but is not in check
            if not self.board.incheck[opposite_colour(self.turn)]:
                # If it is a players turn, they are not in check, but don't have any valid/possible moves
                if self.board.get_out_check(self.turn) == 0:
                    self.tie = True
                    self.game_over = True
                    

            # Check insufficient material stalemate
            # Count up pieces on board
            piecesleft = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]     
            for row in range(SIZE):
                for col in range(SIZE):
                    if self.board.board[row][col] != None:
                        piecesleft[self.board.board[row][col].colour][self.board.board[row][col].kind] += 1

            # If either player has only a king
            if piecesleft[BLACK] == [0, 0, 0, 0, 1, 0]:                 # Black only has king
                opposite = WHITE
            elif piecesleft[WHITE] == [0, 0, 0, 0, 1, 0]:               # White only has king
                opposite = BLACK
            else:
                opposite = -1    # Both players still have more than a king

            # Check what pieces the opposite player has
            if opposite != -1:
                if (piecesleft[opposite] == [0, 0, 0, 0, 1, 0]          # Just king
                or piecesleft[opposite] == [0, 0, 1, 0, 1, 0]           # Just king and 1 bishop
                or  piecesleft[opposite] == [0, 1, 0, 0, 1, 0]):        # Just king and 1 knight
                    self.tie = True
                    self.game_over = True
                                    

def main():
    """Mainline for program"""
    pygame.init()

    # Set up windowsurface
    windowSurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    pygame.display.set_caption('Chess')

    # Setup menu piece images
    blackbishopimage = load_image("black_bishop.png")
    bigbishop = BigBishopImage(blackbishopimage, 25, windowSurface.get_rect().centery)

    blackknightimage = load_image("black_knight.png")
    bigknight = BigKnightImage(blackknightimage, 675, windowSurface.get_rect().centery)

    # To be displayed on menu or instructions (next 4 images)
    # Load the home icon image in
    homeiconimage = load_image("home_icon.png")
    homeicon = HomeIcon(homeiconimage, 5, 960)

    # Load the home icon image in for the menu
    homeiconimage = load_image("home_icon.png")
    menuhomeicon = HomeIcon(homeiconimage, 200, 98)

    # Load the sound icon image in
    soundiconimage = load_image("sound_icon.png")
    soundicon = SoundIcon(soundiconimage, 240 ,100)

    # Load the hint icon image in
    hintimage = load_image("lightbulb.png")
    hinticon = HintIcon(hintimage, 280, 95)

    # Run the main menu
    game = run_main_menu(windowSurface, bigbishop, bigknight, homeicon, hinticon, soundicon, menuhomeicon)

    # Run the game loop
    while True:

        # If you are playing against the AI, run AI logic
        if game.AI:
            # If it is the AIs turn
            if game.turn == BLACK:

                # Run the AI logic and make the AIs move                
                ai = ChessAI()
                stats = ai.get_best_move(game.board, BLACK, game.difficulty, 1000, -1000)
                game.board.make_move(stats[1], stats[2], game.graveyard)

                # Play the sound effect for moving a piece if it is turned on
                if game.soundeffects:
                    game.piecemovesound.play()

                game.board.does_pawn_promote(stats[2][0], stats[2][1])  # Check if pawn needs to be promoted
                game.display_frame(windowSurface)                       # Display the frame again
                game.update_check_conditions()                          # Update game conditions
                game.turn = opposite_colour(BLACK)                      # Change the turn

        # Processes events
        game.process_events(windowSurface)

        # Update the score
        game.whitescore = game.get_score(BLACK)
        game.blackscore = game.get_score(WHITE)
    
        # Displays the frame
        game.display_frame(windowSurface)

        # If game is over, wait ten seconds, then proceed to home menu
        if game.game_over:
            process_win_screen()

        # If game is over or home button clicked return to main menu
        if game.game_over or game.home_button:
            game.home_button = False

            # Run game
            game = run_main_menu(windowSurface, bigbishop, bigknight, homeicon, hinticon, soundicon, menuhomeicon)

main()
