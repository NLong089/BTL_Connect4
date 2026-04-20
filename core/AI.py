import random
from math import inf

from core.board import (
    COLS,
    ROWS,
    board_full,
    drop_piece,
    get_next_open_row,
    is_valid_column,
)
from core.rule_checker import check_winner

AI_PLAYER = 2
HUMAN_PLAYER = 1
EMPTY = 0
WIN_SCORE = 1_000_000
AI_DIFFICULTY_SETTINGS = {
    "easy": {"depth": 2, "random_chance": 0.28, "random_pool": 4},
    "medium": {"depth": 4, "random_chance": 0.12, "random_pool": 3},
    "hard": {"depth": 5, "random_chance": 0.0, "random_pool": 1},
}


def opponent_of(piece):
    return HUMAN_PLAYER if piece == AI_PLAYER else AI_PLAYER


def get_valid_locations(board):
    return [col for col in range(COLS) if is_valid_column(board, col)]


def copy_board(board):
    return [row[:] for row in board]


def simulate_drop(board, col, piece):
    row = get_next_open_row(board, col)
    if row is None:
        return None

    child = copy_board(board)
    drop_piece(child, row, col, piece)
    return child


def iter_windows(board):
    for row in range(ROWS):
        for col in range(COLS - 3):
            yield board[row][col:col + 4]

    for col in range(COLS):
        for row in range(ROWS - 3):
            yield [board[row + offset][col] for offset in range(4)]

    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            yield [board[row + offset][col + offset] for offset in range(4)]

    for row in range(3, ROWS):
        for col in range(COLS - 3):
            yield [board[row - offset][col + offset] for offset in range(4)]


def evaluate_window(window, piece):
    opponent = opponent_of(piece)
    piece_count = window.count(piece)
    opponent_count = window.count(opponent)
    empty_count = window.count(EMPTY)

    if piece_count == 4:
        return WIN_SCORE
    if opponent_count == 4:
        return -WIN_SCORE
    if piece_count == 3 and empty_count == 1:
        return 120
    if piece_count == 2 and empty_count == 2:
        return 14
    if opponent_count == 3 and empty_count == 1:
        return -140
    if opponent_count == 2 and empty_count == 2:
        return -16
    return 0


def score_position(board, piece):
    score = 0
    center_col = COLS // 2
    center_values = [board[row][center_col] for row in range(ROWS)]
    score += center_values.count(piece) * 18

    for window in iter_windows(board):
        score += evaluate_window(window, piece)

    return score


def order_moves(board, piece):
    center_col = COLS // 2
    ordered = []

    for col in get_valid_locations(board):
        child = simulate_drop(board, col, piece)
        if child is None:
            continue

        tactical_bonus = WIN_SCORE if check_winner(child, piece) else 0
        heuristic = score_position(child, piece)
        center_bias = -abs(center_col - col) * 6
        ordered.append((tactical_bonus + heuristic + center_bias, col))

    ordered.sort(key=lambda item: item[0], reverse=True)
    return [col for _, col in ordered]


def is_terminal_node(board):
    return (
        check_winner(board, HUMAN_PLAYER)
        or check_winner(board, AI_PLAYER)
        or board_full(board)
    )


def alpha_beta(board, depth, alpha, beta, maximizing_player):
    ordered_columns = order_moves(
        board,
        AI_PLAYER if maximizing_player else HUMAN_PLAYER,
    )
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if check_winner(board, AI_PLAYER):
            return None, WIN_SCORE + depth
        if check_winner(board, HUMAN_PLAYER):
            return None, -WIN_SCORE - depth
        if board_full(board):
            return None, 0
        return None, score_position(board, AI_PLAYER)

    if maximizing_player:
        value = -inf
        best_col = ordered_columns[0]

        for col in ordered_columns:
            child = simulate_drop(board, col, AI_PLAYER)
            if child is None:
                continue

            _, new_score = alpha_beta(child, depth - 1, alpha, beta, False)
            if new_score > value:
                value = new_score
                best_col = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best_col, int(value)

    value = inf
    best_col = ordered_columns[0]

    for col in ordered_columns:
        child = simulate_drop(board, col, HUMAN_PLAYER)
        if child is None:
            continue

        _, new_score = alpha_beta(child, depth - 1, alpha, beta, True)
        if new_score < value:
            value = new_score
            best_col = col

        beta = min(beta, value)
        if alpha >= beta:
            break

    return best_col, int(value)


def choose_best_move(board, depth):
    valid_columns = get_valid_locations(board)
    if not valid_columns:
        return None

    col, _ = alpha_beta(board, depth, -inf, inf, True)
    return col if col is not None else valid_columns[0]


def get_ai_move(board, difficulty="easy"):
    settings = AI_DIFFICULTY_SETTINGS.get(difficulty, AI_DIFFICULTY_SETTINGS["medium"])
    ordered_columns = order_moves(board, AI_PLAYER)

    if ordered_columns and random.random() < settings["random_chance"]:
        pool_size = min(settings["random_pool"], len(ordered_columns))
        return random.choice(ordered_columns[:pool_size])

    return choose_best_move(board, settings["depth"])
