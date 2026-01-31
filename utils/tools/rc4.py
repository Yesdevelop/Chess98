import numpy as np

class RC4:
    def __init__(self, key):
        self.x = self.y = 0
        self.state = []
        for i in range(256):
            self.state.append(i)
        j = 0
        for i in range(256):
            j = (j + self.state[i] + key[i % len(key)]) & 0xff
            self.swap(i, j)

    def swap(self, i, j):
        t = self.state[i]
        self.state[i] = self.state[j]
        self.state[j] = t

    def nextByte(self):
        self.x = (self.x + 1) & 0xff
        self.y = (self.y + self.state[self.x]) & 0xff
        self.swap(self.x, self.y)
        t = (self.state[self.x] + self.state[self.y]) & 0xff
        return self.state[t]

    def nextLong(self):
        n0 = self.nextByte()
        n1 = self.nextByte()
        n2 = self.nextByte()
        n3 = self.nextByte()
        return ((n0 + (n1 << 8) + (n2 << 16) + ((n3 << 24) & 0xffffffff)) + 2147483648) % 4294967296 - 2147483648


PreGen_zobristKeyPlayer = None
PreGen_zobristLockPlayer = None
PreGen_zobristKeyTable = []
PreGen_zobristLockTable = []

rc4 = RC4([0])

PreGen_zobristKeyPlayer = rc4.nextLong()
rc4.nextLong()
PreGen_zobristLockPlayer = rc4.nextLong()

for i in range(14):
    keys = []
    locks = []
    for j in range(256):
        keys.append(rc4.nextLong())
        rc4.nextLong()
        locks.append(rc4.nextLong())
    PreGen_zobristKeyTable.append(keys)
    PreGen_zobristLockTable.append(locks)

# 棋子序号对应的棋子类型
# ElephantEye的棋子序号从0到47, 其中0到15不用, 16到31表示红子, 32到47表示黑子。
# 每方的棋子顺序依次是：帅仕仕相相马马车车炮炮兵兵兵兵兵(将士士象象马马车车炮炮卒卒卒卒卒)
# 提示：判断棋子是红子用"pc < 32", 黑子用"pc >= 32"
#
# const int cnPieceTypes[48] = {
#     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#     0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 6, 6,
#     0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 6, 6
# };

print(PreGen_zobristKeyPlayer)
print(PreGen_zobristLockPlayer)


mat = PreGen_zobristKeyTable[13]

#mat = PreGen_zobristLockTable[13]

mat = np.asarray(mat,dtype=np.int32)
mat = mat.reshape(16,16)
mat = mat.T.T.T
mat = np.fliplr(mat)

mat = mat[3:12]
mat = list(mat)

for i,line in enumerate(mat):
    mat[i] = list(line[3:13])

for line in mat:
    _str = ""
    for p in line:
        _str += f"{p},"
    _str = _str[:len(_str) - 1]
    print("{" + _str + "},")

# for i in range(14):
#     print(PreGen_zobristKeyTable[i][51])
#     print(PreGen_zobristLockTable[i][51])
