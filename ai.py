
from engine import check_winner, make_move


from engine import get_legal_moves
import random
zobrist_active = [random.getrandbits(64) for _ in range(10)]
zobrist_table = [[[random.getrandbits(64) for _ in range(2)] for _ in range(9)] for _ in range(9)]
transposition_table = {}

nodes_searched = 0




# ── "Best-First" Move Ordering ──────────────────────────────────────────
def score_move(board,meta,sub,local,player):
    score = 0
    if local == 4:
        score += 50
    if local in [0,2,6,8]:
        score += 20
    temp = board[sub][local]
    board[sub][local] = player
    if check_winner(board[sub]) == player:
        score += 1000
    board[sub][local] = temp
    return score

# ── ZOBRIST TABLE ──────────────────────────────────────────
def compute_hash(board, active_sub):
    h = 0
    for sub in range(9):
        for local in range(9):
            if board[sub][local] == 1:
                h^= zobrist_table[sub][local][0]
            elif board[sub][local] == -1:
                h^= zobrist_table[sub][local][1]
    if active_sub == -1:
        h ^= zobrist_active[9]
    else:
        h ^= zobrist_active[active_sub]
    return h




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
def evaluate(board, meta, active_sub,depth, turn, profile):
    
    score = 0
    
    if profile == "Aggressive":
        meta_threat_weight = 800
        piece_weight = 2
    elif profile == "Balanced":
        meta_threat_weight = 800
        piece_weight = 5    
    winner = check_winner(meta)
    if winner != 0:
        return winner*(15000+depth)
    meta_weights = [150,100,150,100,250,100,150,100,150]
    sub_is_free = (
            active_sub == -1 or meta[active_sub] != 0 or all(board[active_sub][c] != 0 for c in range(9))
    )

    if sub_is_free:
        for s in range(9):
            if meta[s] == 0:
                score -= detect_threats(board[s],-turn)*50
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

    score += detect_threats(meta, 1) * meta_threat_weight
    score -= detect_threats(meta, -1) * meta_threat_weight
    for s in range(9):
        for c in range(9):
            if board[s][c] == 1:
                score += piece_weight
            elif board[s][c] == -1:
                score -= piece_weight

    return score


# ── MOVE SELECTION ────────────────────────────────────────────
def best_moves(board,meta, active_sub ,player):
    if active_sub == -1:
        available = [s for s in range(9) if meta[s] == 0 and any(board[s][c] == 0 for c in range(9))]
        active_sub = random.choice(available)
    if find_winning_moves(board, meta,active_sub,player) != -1:
        return find_winning_moves(board, meta,active_sub, player)
    block = find_winning_moves(board, meta,active_sub, player*(-1))
    if block != -1:
        return block
    priority = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    for a in priority:
        if board[active_sub][a] == 0:
            return (active_sub, a)




# ── MINIMAX + ALPHA-BETA PRUNING ──────────────────────────────
def minimax(board,meta,active_sub,turn,depth, alpha,beta, profile):
    global nodes_searched
    nodes_searched += 1
    h = compute_hash(board, active_sub)
    if h in transposition_table:
        return transposition_table[h]
    winner = check_winner(meta)
    if winner != 0 :
        return winner*(15000+depth)
    if depth == 0:
        return evaluate(board, meta,active_sub, depth, turn, profile)
    moves = get_legal_moves(board,meta,active_sub)
    moves.sort(key=lambda m: score_move(board,meta,m[0],m[1],turn), reverse=(turn==1))
    if turn == 1:
        best = -float('inf')
        for sub, local in moves:
            temp = board[sub][local]
            temp1 = meta[sub]
            old_active = active_sub
            make_move(board, meta, sub, local, turn, active_sub)
            score = minimax(board, meta, local, -turn, depth - 1, alpha,beta, profile)
            board[sub][local] = temp
            meta[sub] = temp1
            active_sub = old_active
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
    elif turn == -1:
        best = float('inf')
        for sub, local in moves:
            temp = board[sub][local]
            temp1 = meta[sub]
            old_active = active_sub
            make_move(board, meta, sub, local, turn, active_sub)
            score = minimax(board, meta, local, -turn, depth - 1, alpha, beta, profile)
            board[sub][local] = temp
            meta[sub] = temp1
            active_sub = old_active
            best = min(best, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
    transposition_table[h] = best
    return best



# ── Best move ──────────────────────────────────────────
def get_best_move(board, meta, active_sub, depth, profile):
    moves_played = sum(1 for s in range(9) for c in range(9) if board[s][c] != 0)
    if moves_played == 0:
        return (4, 4), 0
    if moves_played == 1 and board[4][4] != 0:
        return (4, 0), 0
    moves = get_legal_moves(board,meta,active_sub)
    if not moves:
        return None, 0
    candidate = best_moves(board, meta, active_sub, -1)
    if candidate in moves:
        moves.remove(candidate)
        moves.insert(0, candidate)
    best_score = float('inf')
    best_move = None
    for sub, local in moves:
        temp = board[sub][local]
        temp1 = meta[sub]
        old_active = active_sub  
        make_move(board, meta, sub, local, -1, active_sub)
        score = minimax(board, meta, local, 1, depth - 1,-float('inf'),float('inf'),profile)
        board[sub][local] = temp
        meta[sub] = temp1
        active_sub = old_active
        if score < best_score:
            best_score = score
            best_move = (sub, local)
    return best_move, best_score


