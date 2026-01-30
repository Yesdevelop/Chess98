# board.py
import numpy as np

# 棋子编码（保持不变）
EMPTY = 0
R_KING, R_GUARD, R_BISHOP, R_KNIGHT, R_ROOK, R_CANNON, R_PAWN = 1, 2, 3, 4, 5, 6, 7
B_KING, B_GUARD, B_BISHOP, B_KNIGHT, B_ROOK, B_CANNON, B_PAWN = -1, -2, -3, -4, -5, -6, -7
Red, Black = 1, 0

def fen_to_matrix(fen: str) -> np.ndarray:
    """将中国象棋 FEN 字符串转换为 7×9×10 的输入张量"""
    PIECE_TO_INT = {
        'K': R_KING, 'A': R_GUARD, 'B': R_BISHOP, 'N': R_KNIGHT, 'R': R_ROOK, 'C': R_CANNON, 'P': R_PAWN,
        'k': B_KING, 'a': B_GUARD, 'b': B_BISHOP, 'n': B_KNIGHT, 'r': B_ROOK, 'c': B_CANNON, 'p': B_PAWN,
    }

    board = np.zeros((10, 9), dtype=int)
    rows = fen.split('/')
    if len(rows) != 10:
        raise ValueError("FEN 棋盘部分应为10行，用'/'分隔")

    rows[-1] = rows[-1].strip().split()[0]  # 去除元信息

    for y in range(10):
        x = 0
        for c in rows[y]:
            if c.isdigit():
                x += int(c)
            elif c in PIECE_TO_INT:
                if x < 9:
                    board[y, x] = PIECE_TO_INT[c]
                    x += 1
                else:
                    raise ValueError(f"列溢出：y={y}, x={x}, 棋子={c}")
            else:
                raise ValueError(f"未知字符: {c}")

    output = np.zeros((7, 9, 10), dtype=int)
    for y in range(10):
        for x in range(9):
            piece = board[y, x]
            if piece == EMPTY:
                continue
            channel = abs(piece) - 1
            sign = 1 if piece > 0 else -1
            output[channel, x, y] = sign

    # 结果要额外翻转一遍
    output = np.flip(output, axis=2)  # y轴翻转

    return output

def matrix_to_fen(matrix: np.ndarray) -> str:
    """将 7×9×10 的张量转换为 FEN 字符串"""
    PIECE_TO_CHAR = {
        R_KING: 'K', R_GUARD: 'A', R_BISHOP: 'B', R_KNIGHT: 'N', R_ROOK: 'R', R_CANNON: 'C', R_PAWN: 'P',
        B_KING: 'k', B_GUARD: 'a', B_BISHOP: 'b', B_KNIGHT: 'n', B_ROOK: 'r', B_CANNON: 'c', B_PAWN: 'p',
    }

    rows = []
    for y in range(10):
        row = []
        empty_count = 0
        for x in range(9):
            for channel in range(7):
                piece = matrix[channel, x, y]
                if piece != 0:
                    if empty_count > 0:
                        row.append(str(empty_count))
                        empty_count = 0
                    row.append(PIECE_TO_CHAR[piece])
                    break
            else:
                empty_count += 1
        if empty_count > 0:
            row.append(str(empty_count))
        rows.append(''.join(row))

    return '/'.join(rows) + " w - - 0"

class Situation:
    """棋局状态类，支持翻转增强 → 返回新对象"""
    def __init__(self, fen: str):
        self.fen = fen
        self.actor_flag = Red if "w" in fen else Black
        self.matrix = fen_to_matrix(fen)

    def __str__(self):
        return f"Situation(actor_flag={self.actor_flag}, matrix_shape={self.matrix.shape})"

    def flip_left_and_right(self):
        """左右翻转：返回新对象"""
        new = object.__new__(Situation)
        new.fen = None
        new.actor_flag = self.actor_flag
        new.matrix = self.matrix[:, ::-1, :].copy()  # x轴反转
        return new

    def flip_up_and_down(self):
        """上下翻转 + 颜色反转 + 切换走子方：返回新对象"""
        new = object.__new__(Situation)
        new.fen = None
        new.actor_flag = 1 - self.actor_flag  # 轮到对方走
        new.matrix = (-self.matrix)[:, :, ::-1].copy()  # 颜色反转 + y轴反转
        return new

    def do_move(self, move: int):
        new = object.__new__(Situation)
        new.matrix = self.matrix.copy()
        new.fen = None
        new.actor_flag = 1 - self.actor_flag
        move_str = str(move).zfill(4)
        x1 = int(move_str[0])
        y1 = int(move_str[1])
        x2 = int(move_str[2])
        y2 = int(move_str[3])

        captured = {'i': 0, 'obj': 0}
        for i in range(7):
            if new.matrix[i, x2, y2] != 0:
                captured['i'] = i
                captured['obj'] = new.matrix[i, x2, y2]
            if new.matrix[i, x1, y1] != 0:
                new.matrix[i, x2, y2] = new.matrix[i, x1, y1]
                new.matrix[i, x1, y1] = 0

        return new, captured

    def undo_move(self, move: int, captured: dict):
        new = object.__new__(Situation)
        new.matrix = self.matrix.copy()
        new.fen = None
        new.actor_flag = 1 - self.actor_flag
        move_str = str(move).zfill(4)
        x1 = int(move_str[0])
        y1 = int(move_str[1])
        x2 = int(move_str[2])
        y2 = int(move_str[3])

        for i in range(7):
            if new.matrix[i, x2, y2] != 0:
                new.matrix[i, x1, y1] = new.matrix[i, x2, y2]
                new.matrix[i, x2, y2] = 0
        new.matrix[captured['i'], x2, y2] = captured['obj']

        return new

if __name__ == "__main__":
    test_fen = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0'
    s1 = Situation(fen=test_fen)
    s2, captured = s1.do_move(1)
    print(s2.matrix)
    s3 = s2.undo_move(1, captured)
    print(s3.matrix)
