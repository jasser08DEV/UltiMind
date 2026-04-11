import random


from engine import check_winner, make_move


from engine import get_legal_moves


nodes_searched = 0


# ── THREAT DETECTION ──────────────────────────────────────────
def detect_threats(cells, player):
    threats = 0
    lines=[
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in lines:
        vals = [cells[a],cells[b],cells[c]]
        if vals.count(player) == 2 and vals.count(0)==1:
            threats += 1
    return threats


def winning_moves(board, active_sub, player):
    lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in lines:
        if board[active_sub][a] == player and board[active_sub][b] == player and board[active_sub][c] == 0:
            return (active_sub, c)
        elif board[active_sub][a] == player and board[active_sub][c] == player and board[active_sub][b] == 0:
            return (active_sub, b)
        elif board[active_sub][b] == player and board[active_sub][c] == player and board[active_sub][a] == 0:
            return (active_sub, a)
    return -1

# ── WIN/BLOCK FINDER ──────────────────────────────────────────
def find_winning_moves(board, meta, active_sub, player):
    if active_sub == -1:
        for s in range(9):
            if meta[s] == 0:
                win = winning_moves(board,s, player)
                if win != -1:
                    return win
    else:
        win = winning_moves(board,active_sub, player)
        if win != -1:
            return win
    return -1





# ── HEURISTIC EVALUATION ──────────────────────────────────────
def evaluate(board, meta, active_sub,depth, turn):
    score = 0
    winner = check_winner(meta)
    if winner != 0:
        return winner*(15000+depth)
    meta_weights = [150,100,150,100,250,100,150,100,150]
    sub_is_free = (
            active_sub == -1 or meta[active_sub] != 0 or all(board[active_sub][c] != 0 for c in range(9))
    )
    if not sub_is_free:
            score -= detect_threats(board[active_sub], -turn) *100
    for i in range(9):
        if meta[i] == 1:
            score += meta_weights[i]
        elif meta[i] == -1:
            score -= meta_weights[i]
        elif meta[i] == 0:
            score += detect_threats(board[i],1)*30
            score -= detect_threats(board[i],-1)*30

    score += detect_threats(meta, 1) * 400
    score -= detect_threats(meta, -1) * 400
    for s in range(9):
        for c in range(9):
            if board[s][c] == 1:
                score += 5
            elif board[s][c] == -1:
                score -= 5

    return score


# ── MOVE SELECTION ────────────────────────────────────────────
def best_moves(board,meta, active_sub ,player):
    if active_sub == -1:
        available = [s for s in range(9) if meta[s] == 0 and any(board[s][c] == 0 for c in range(9))]
        active_sub = random.choice(available)
    best_move = (0,0)
    odd = []
    even = []

    if find_winning_moves(board, meta,active_sub,player) != -1:
        return find_winning_moves(board, meta,active_sub, player)
    block = find_winning_moves(board, meta,active_sub, player*(-1))
    if block != -1:
        return block

    for a in range(9):
        if board[active_sub][a] == 0 and a % 2 == 0:
            even.append(a)
        elif board[active_sub][a] == 0:
            odd.append(a)
    if 4 in even:
        best_move = (active_sub,4)
    elif even != []:
        n = random.choice(even)
        best_move = (active_sub,n)
    else:
        n = random.choice(odd)
        best_move = (active_sub,n)
    return best_move



# ── MINIMAX + ALPHA-BETA PRUNING ──────────────────────────────
def minimax(board,meta,active_sub,turn,depth, alpha,beta):
    global nodes_searched
    nodes_searched += 1
    winner = check_winner(meta)
    if winner != 0 :
        return winner*(15000+depth)
    if depth == 0:
        return evaluate(board, meta,active_sub, depth, turn)
    moves = get_legal_moves(board,meta,active_sub)
    if turn == 1:
        best = -float('inf')
        for sub, local in moves:
            temp = board[sub][local]
            temp1 = meta[sub]
            make_move(board, meta, sub, local, turn, active_sub)
            score = minimax(board, meta, local, -turn, depth - 1, alpha,beta)
            board[sub][local] = temp
            meta[sub] = temp1
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    elif turn == -1:
        best = float('inf')
        for sub, local in moves:
            temp = board[sub][local]
            temp1 = meta[sub]
            make_move(board, meta, sub, local, turn, active_sub)
            score = minimax(board, meta, local, -turn, depth - 1, alpha, beta)
            board[sub][local] = temp
            meta[sub] = temp1
            best = min(best, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return best



# ── ENTRY POINT ────────────────────────────────────────────
def get_best_move(board, meta, active_sub, depth):
    best_score = float('inf')
    best_move = None
    moves = get_legal_moves(board,meta,active_sub)
    candidate = best_moves(board, meta, active_sub, -1)
    if candidate in moves:
        moves.remove(candidate)
        moves.insert(0, candidate)
    for sub, local in moves:
        temp = board[sub][local]
        temp1 = meta[sub]
        make_move(board, meta, sub, local, -1, active_sub)
        score = minimax(board, meta, local, 1, depth - 1,-float('inf'),float('inf'))
        board[sub][local] = temp
        meta[sub] = temp1
        if score < best_score:
            best_score = score
            best_move = (sub, local)
    return best_move


