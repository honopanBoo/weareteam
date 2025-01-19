import math
import copy

BLACK = 1
WHITE = 2

# 初期盤面
board = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 0, 0],
    [0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
]

def can_place_x_y(board, stone, x, y):
    if board[y][x] != 0:
        return False  # 既に石がある場合は置けない

    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == opponent:
            nx += dx
            ny += dy
            found_opponent = True

        if found_opponent and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == stone:
            return True

    return False

def can_place(board, stone):
    valid_moves = []
    for y in range(len(board)):
        for x in range(len(board[0])):
            if can_place_x_y(board, stone, x, y):
                valid_moves.append((x, y))
    return valid_moves

def get_game_phase(board):
    stone_count = sum(cell != 0 for row in board for cell in row)
    if stone_count < 20:
        return "early"
    elif stone_count < 40:
        return "mid"
    else:
        return "late"

def get_score_map(game_phase):
    if game_phase == "early":
        return [
            [50, -5, 3, 3, -5, 50],
            [-5, -15, 1, 1, -15, -5],
            [ 3,   1,  0,  0,   1,  3],
            [ 3,   1,  0,  0,   1,  3],
            [-5, -15, 1, 1, -15, -5],
            [50, -5, 3, 3, -5, 50],
        ]
    elif game_phase == "mid":
        return [
            [50, -10, 7, 7, -10, 50],
            [-10, -20, 2, 2, -20, -10],
            [ 7,   2, 5, 5,   2,  7],
            [ 7,   2, 5, 5,   2,  7],
            [-10, -20, 2, 2, -20, -10],
            [50, -10, 7, 7, -10, 50],
        ]
    elif game_phase == "late":
        return [
            [100, -20, 20, 20, -20, 100],
            [-20, -30, 15, 15, -30, -20],
            [ 20,  15, 16, 16,  15,  20],
            [ 20,  15, 16, 16,  15,  20],
            [-20, -30, 15, 15, -30, -20],
            [100, -20, 20, 20, -20, 100],
        ]

def apply_move(board, stone, x, y):
    new_board = copy.deepcopy(board)
    new_board[y][x] = stone
    opponent = 3 - stone
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        stones_to_flip = []

        while 0 <= nx < len(board[0]) and 0 <= ny < len(board) and new_board[ny][nx] == opponent:
            stones_to_flip.append((nx, ny))
            nx += dx
            ny += dy

        if stones_to_flip and 0 <= nx < len(board[0]) and 0 <= ny < len(board) and new_board[ny][nx] == stone:
            for fx, fy in stones_to_flip:
                new_board[fy][fx] = stone

    return new_board

def count_stable_discs(board, stone):
    stable_discs = 0
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                is_stable = True
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    while 0 <= nx < len(board[0]) and 0 <= ny < len(board):
                        if board[ny][nx] == 0:  # 空白があれば安定ではない
                            is_stable = False
                            break
                        nx += dx
                        ny += dy
                    if not is_stable:
                        break
                if is_stable:
                    stable_discs += 1
    return stable_discs

def evaluate_board(board, stone):
    game_phase = get_game_phase(board)
    score_map = get_score_map(game_phase)

    score = 0
    black_count = 0
    white_count = 0

    # 盤面を評価しつつ石の数をカウント
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == stone:
                score += score_map[y][x]
                black_count += 1  # 黒石の場合は黒の数をカウント
            elif board[y][x] == 3 - stone:
                score -= score_map[y][x]
                white_count += 1  # 白石の場合は白の数をカウント

    # 石の数を評価に追加（黒石が多ければプラス、白石が多ければマイナス）
    score += (black_count - white_count) * 5  # 5は重み（調整可能）

    # 安定石を考慮
    stable_score = count_stable_discs(board, stone) - count_stable_discs(board, 3 - stone)
    score += stable_score * 11  # 安定石を重視する重み（10は調整可能）

    # 合法手の数を加味する
    valid_moves = can_place(board, stone)
    score += len(valid_moves) * 6  # 合法手が多ければスコアが増加（6は重み）

    # 序盤ではポジションと手数を重視、終盤では安定石と石の数を重視
    if game_phase == "early":
        score += len(valid_moves) * 6  # 合法手が多ければスコア増加
    elif game_phase == "late":
        score += (black_count - white_count) * 10  # 終盤では石の数を重視

    return score

def get_dynamic_depth(board):
    stone_count = sum(cell != 0 for row in board for cell in row)
    if stone_count < 20:
        return 6  # 序盤は浅い
    elif stone_count < 40:
        return 6  # 中盤は通常
    else:
        return 7  # 終盤は深い

def minimax(board, stone, depth, alpha, beta, maximizing_player):
    if depth == 0 or not can_place(board, stone):
        return evaluate_board(board, stone), None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for y in range(len(board)):
            for x in range(len(board[0])):
                if can_place_x_y(board, stone, x, y):
                    new_board = apply_move(board, stone, x, y)
                    eval, _ = minimax(new_board, 3 - stone, depth - 1, alpha, beta, False)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = (x, y)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for y in range(len(board)):
            for x in range(len(board[0])):
                if can_place_x_y(board, stone, x, y):
                    new_board = apply_move(board, stone, x, y)
                    eval, _ = minimax(new_board, 3 - stone, depth - 1, alpha, beta, True)
                    if eval < min_eval:
                        min_eval = eval
                        best_move = (x, y)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval, best_move

class WolfAI(object):

    def face(self):
        return "🐺"

    def place(self, board, stone):
        depth = get_dynamic_depth(board)
        _, move = minimax(board, stone, depth=depth, alpha=-math.inf, beta=math.inf, maximizing_player=True)
        return move
