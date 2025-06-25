from Game2048 import BasePlayer

class Player(BasePlayer):
    CORNER_IDS = (0, 3, 12, 15)
    CENTER_IDS = (5, 6, 9, 10)
    TILE_GRADIENT = [
        2**15, 2**14, 2**13, 2**12,
        2**8,  2**9,  2**10, 2**11,
        2**7,  2**6,  2**5,  2**4,
        2**0,  2**1,  2**2,  2**3
    ]
    PENALTY_ORDER = (12, 8, 4, 0, 1, 2, 3, 7, 11, 15, 14, 13, 9, 5, 6, 10)
    MOVE_PREFERENCES = ('R', 'U', 'L', 'D')

    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self.node_count    = 0
        self.parent_count  = 0
        self.child_count   = 0
        self.depth_count   = 0
        self.move_count    = 0

    def findMove(self, state):
        self.move_count += 1
        legal_moves = list(state.actions())
        best_move   = legal_moves[0] if legal_moves else 'L'
        best_score  = float('-inf')
        depth       = 1

        try:
            while self.timeRemaining():
                self.depth_count  += 1
                self.parent_count += 1
                self.node_count   += 1

                for mv in legal_moves:
                    if not self.timeRemaining():
                        break
                    nxt_state = state.move(mv)
                    score     = self.chance_node(nxt_state, depth - 1)
                    if score is not None and score > best_score:
                        best_score, best_move = score, mv

                self.setMove(best_move)
                print(f"[Depth {depth}] Best≈{best_score:.1f} via {best_move}")
                depth += 1

        finally:
            if best_move not in legal_moves and legal_moves:
                best_move = legal_moves[0]
            self.setMove(best_move)

    def max_node(self, state, depth):
        self.node_count  += 1
        self.child_count += 1

        if state.gameOver():
            return state.getScore()
        if depth <= 0:
            return self.evaluate(state)

        self.parent_count += 1
        best = float('-inf')
        for mv in self.moveOrder(state):
            if not self.timeRemaining():
                return None
            nxt   = state.move(mv)
            score = self.chance_node(nxt, depth - 1)
            if score is None:
                return None
            best = max(best, score)
        return best

    def chance_node(self, state, depth):
        self.node_count  += 1
        self.child_count += 1

        if state.gameOver():
            return state.getScore()
        if depth <= 0:
            return self.evaluate(state)

        total = 0
        for pos, tile in state.possibleTiles():
            if not self.timeRemaining():
                return None
            spawned = state.addTile(pos, tile)
            prob = 0.9 if tile == 1 else 0.1
            val = self.max_node(spawned, depth - 1)
            if val is None:
                return None
            total += prob * val

        return total

    def evaluate(self, state):
        board = state._board
        base = state.getScore()

        # Reward for empty tile
        empties= board.count(0)
        empty_b = empties * 500

        # Reward for placing maximum tile on the corner and if not than penalty
        maximum = max(board)
        corner_b = 3000 if any(board[i] == maximum for i in Player.CORNER_IDS) else -2000

        # Tile‐gradient weights
        tile_s = sum((2**board[i]) * Player.TILE_GRADIENT[i]
            for i in range(16) if board[i] > 0) * 0.00005

        # Monotonicity
        def monotonic(line):
            return all(line[i] >= line[i+1] for i in range(len(line)-1)) \
                or all(line[i] <= line[i+1] for i in range(len(line)-1))

        mono_s = 0
        for r in range(4):
            row = board[r*4:(r+1)*4]
            col = board[r::4]
            if monotonic(row):
                mono_s += 600
            if monotonic(col):
                mono_s += 600

        # Merging Possibility and reward
        merges = 0
        for i in range(16):
            v = board[i]
            if v == 0:
                continue
            if (i % 4) < 3 and board[i+1] == v:
                merges += 1
            if i < 12 and board[i+4] == v:
                merges += 1
        merge_s = merges * 200

        # Penalty for not following the heuristics evaluation fuction
        penalty = 0
        for i in range(16):
            if board[i] >= maximum - 2 and i not in Player.PENALTY_ORDER:
                penalty -= 2000

        return base + empty_b + corner_b + tile_s + mono_s + merge_s + penalty

    def moveOrder(self, state):
        prefs = Player.MOVE_PREFERENCES
        legal = set(state.actions())
        return [m for m in prefs if m in legal]

    def stats(self):
        avg_depth = self.depth_count / max(1, self.move_count)
        bf = self.child_count / max(1, self.parent_count)
        print(f"AvgDepth={avg_depth:.2f}, Branching={bf:.2f}")
