from core.board import ROWS, COLS

def check_winner(board, player):
    # ngang
    for r in range(ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == player and
                board[r][c + 1] == player and
                board[r][c + 2] == player and
                board[r][c + 3] == player):
                return True

    # dọc
    for r in range(ROWS - 3):
        for c in range(COLS):
            if (board[r][c] == player and
                board[r + 1][c] == player and
                board[r + 2][c] == player and
                board[r + 3][c] == player):
                return True

    # chéo xuống phải
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if (board[r][c] == player and
                board[r + 1][c + 1] == player and
                board[r + 2][c + 2] == player and
                board[r + 3][c + 3] == player):
                return True

    # chéo lên phải
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == player and
                board[r - 1][c + 1] == player and
                board[r - 2][c + 2] == player and
                board[r - 3][c + 3] == player):
                return True

    return False