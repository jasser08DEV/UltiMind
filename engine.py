

def get_legal_moves(board, meta, active_sub):
    if check_winner(meta) != 0:
        return []
    if active_sub != -1:
        if meta[active_sub] != 0 or all(board[active_sub][c] != 0 for c in range(9)):
            active_sub = -1
        sub = [active_sub] if active_sub != -1 else [s for s in range(9) if meta[s] == 0]
    else:
        sub = [s for s in range(9) if meta[s]==0]
    moves = []
    for s in sub:
        for x in range(9):
            if board[s][x] == 0:
                moves.append((s,x))
    return moves

def check_winner(cells):
    p1_mask = 0
    p2_mask = 0
    
    for i in range(9):
        if cells[i] == 1: 
            p1_mask |= (1 << i)
        elif cells[i] == -1: 
            p2_mask |= (1 << i)

    win_masks = [7, 56, 448, 73, 146, 292, 273, 84] 

    for mask in win_masks:
        if (p1_mask & mask) == mask: 
            return 1
        if (p2_mask & mask) == mask: 
            return -1
            
    return 0

def make_move(board,meta, sub,local,turn,active_sub):
    if meta[sub]!=0:
        return turn, active_sub, 0
    if active_sub != -1 and sub != active_sub:
        return turn, active_sub,0
    if board[sub][local] != 0:
        return turn, active_sub,0
    board[sub][local] = turn
    meta[sub] = check_winner(board[sub])
    winner = check_winner(meta)
    turn = turn *(-1)
    active_sub = local
    return turn, active_sub, winner


