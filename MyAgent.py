from Game2048 import *
import random
import math

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)

    def findMove(self, game):
        selectedMove = None
        maxScore = float('-inf')

        for move in game.actions():
            futureGame, _ = game.result(move)
            currentScore = self.calculateScore(futureGame)

            if currentScore > maxScore:
                maxScore = currentScore
                selectedMove = move

        self.setMove(selectedMove)

    def calculateScore(self, board):
        empty = sum(1 for tile in board._board if tile == 0)
        maxTile = max(board._board)
        smooth = self.getSmoothness(board)
        mono = self.getMonotonicity(board)
        corner = self.maxInCorner(board)
        weight = self.weightedPlacement(board)

        return (
            100 * empty +
            1.0 * smooth +
            2.0 * mono +
            2000 * corner +
            1.2 * weight +
            math.log(maxTile + 1, 2)
        )

    def getSmoothness(self, board):
        total = 0
        for i in range(4):
            for j in range(3):
                total -= abs(board.getTile(i, j) - board.getTile(i, j + 1))
        for j in range(4):
            for i in range(3):
                total -= abs(board.getTile(i, j) - board.getTile(i + 1, j))
        return total

    def getMonotonicity(self, board):
        vals = [0, 0, 0, 0]

        for i in range(4):
            for j in range(3):
                a = board.getTile(i, j)
                b = board.getTile(i, j + 1)
                if a > b:
                    vals[0] += b - a
                elif b > a:
                    vals[1] += a - b

        for j in range(4):
            for i in range(3):
                a = board.getTile(i, j)
                b = board.getTile(i + 1, j)
                if a > b:
                    vals[2] += b - a
                elif b > a:
                    vals[3] += a - b

        return max(vals[0], vals[1]) + max(vals[2], vals[3])

    def maxInCorner(self, board):
        m = max(board._board)
        corners = [board.getTile(0, 0), board.getTile(0, 3), board.getTile(3, 0), board.getTile(3, 3)]
        return 1 if m in corners else 0

    def weightedPlacement(self, board):
        weights = [
            [32768, 16384, 8192, 4096],
            [256, 512, 1024, 2048],
            [128, 64, 32, 16],
            [2, 4, 8, 1]
        ]
        score = 0
        for i in range(4):
            for j in range(4):
                score += board.getTile(i, j) * weights[i][j]
        return score
