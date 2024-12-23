import random
import time
import math
from functools import lru_cache


class WeareteamAI:
    def __init__(self):
        # 初期化
        self.board = self.initialize_board()
        self.ZOBRIST_TABLE = [
            [[random.randint(0, 2**64 - 1) for _ in range(2)] for _ in range(8)]
            for _ in range(8)
        ]

    @lru_cache(maxsize=None)
    def zobrist_hash(self, player):
        h = 0
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == '●':
                    h ^= self.ZOBRIST_TABLE[i][j][0]
                elif self.board[i][j] == '○':
                    h ^= self.ZOBRIST_TABLE[i][j][1]
        if player == '○':
            h ^= random.randint(0, 2**64 - 1)
        return h

    def initialize_board(self):
        board = [['.' for _ in range(8)] for _ in range(8)]
        board[3][3] = '○'
        board[3][4] = '●'
        board[4][3] = '●'
        board[4][4] = '○'
        return board

    def print_board(self):
        print("   ａ ｂ ｃ ｄ ｅ ｆ ｇ ｈ")
        for i in range(8):
            row = f"{i + 1:>2} "
            for j in range(8):
                row += self.board[i][j] + ' '
            print(row)

    def is_valid_move(self, row, col, player):
        if self.board[row][col] != '.':
            return False

        opponent = '●' if player == '○' else '○'
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            has_opponent_between = False

            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                r += dr
                c += dc
                has_opponent_between = True

            if has_opponent_between and 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                return True

        return False

    def get_valid_moves(self, player):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col, player):
                    valid_moves.append((row, col))
        return valid_moves

    def place(self, row, col, player):
        self.board[row][col] = player
        opponent = '●' if player == '○' else '○'
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            stones_to_flip = []

            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                stones_to_flip.append((r, c))
                r += dr
                c += dc

            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                for rr, cc in stones_to_flip:
                    self.board[rr][cc] = player

    def evaluate_board(self, player):
        opponent = '●' if player == '○' else '○'
        weights = [
            [100, -20, 10,  5,  5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [ 10,  -2,  1,  1,  1,  1,  -2,  10],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [ 10,  -2,  1,  1,  1,  1,  -2,  10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10,  5,  5, 10, -20, 100]
        ]

        score = 0

        for i in range(8):
            for j in range(8):
                if self.board[i][j] == player:
                    score += weights[i][j]
                elif self.board[i][j] == opponent:
                    score -= weights[i][j]

        return score

    def ai_move(self, player):
        valid_moves = self.get_valid_moves(player)
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_move = None

        for move in valid_moves:
            row, col = move
            temp_board = [row[:] for row in self.board]
            self.place(row, col, player)
            score = self.evaluate_board(player)
            if score > best_score:
                best_score = score
                best_move = move
            self.board = temp_board  # 元の状態に戻す

        return best_move

    def count_stones(self):
        black_count = sum(row.count('●') for row in self.board)
        white_count = sum(row.count('○') for row in self.board)
        return black_count, white_count

    def play_game(self):
        print("オセロを開始します！")
        player_choice = input("先手(黒●)と後手(白○)のどちらを選びますか？(先手:1, 後手:2): ")
        player = '●' if player_choice == "1" else '○'
        ai = '○' if player == '●' else '●'

        current_player = '●'

        while True:
            self.print_board()
            valid_moves = self.get_valid_moves(current_player)

            if not valid_moves:
                print(f"{current_player}に有効な手がありません。ターンをスキップします。")
                current_player = '○' if current_player == '●' else '●'
                continue

            if current_player == player:
                while True:
                    move = input("あなたの手を入力してください（例: d3）: ")
                    if len(move) == 2 and move[0] in "abcdefgh" and move[1] in "12345678":
                        col = ord(move[0]) - ord('a')
                        row = int(move[1]) - 1

                        if (row, col) in valid_moves:
                            self.place(row, col, current_player)
                            break
                    print("無効な手です。もう一度入力してください。")
            else:
                print("AIが手を考えています...")
                move = self.ai_move(current_player)
                if move:
                    self.place(move[0], move[1], current_player)
                    print(f"AIが置いた位置：{chr(move[1] + ord('a'))}{move[0] + 1}")

            current_player = '○' if current_player == '●' else '●'

            if not self.get_valid_moves('●') and not self.get_valid_moves('○'):
                print("ゲーム終了！")
                break

        self.print_board()
        black_count, white_count = self.count_stones()
        print(f"最終結果: 黒●={black_count}, 白○={white_count}")
        if black_count > white_count:
            print("黒●の勝利です！")
        elif white_count > black_count:
            print("白○の勝利です！")
        else:
            print("引き分けです！")


if __name__ == "__main__":
    game = WeareteamAI()
    game.play_game()
