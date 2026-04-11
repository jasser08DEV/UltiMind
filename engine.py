

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
    lines=[
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in lines:
        if cells[a]!=0 and cells[a] == cells[b] == cells[c]:
            return cells[a]
    return 0

def make_move(board,meta, sub,local,turn,active_sub):
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


