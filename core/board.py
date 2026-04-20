ROWS = 6
COLS = 7

def create_board():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def is_valid_column(board, col):
    return 0 <= col < COLS and board[0][col] == 0

def get_next_open_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == 0:
            return row
    return None

def drop_piece(board, row, col, player):
    board[row][col] = player

def board_full(board):
    for c in range(COLS):
        if board[0][c] == 0:
            return False
    return True