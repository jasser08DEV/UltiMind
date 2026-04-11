import pygame
import sys
from engine import make_move
from ai import get_best_move
from ai import nodes_searched
pygame.init()

screen = pygame.display.set_mode((980, 720))
pygame.display.set_caption("UltiMind")
clock = pygame.time.Clock()

BOARD_LEFT = 30
BOARD_TOP = 80
BOARD_SIZE = 540
CELL_SIZE = 60
SUB_SIZE = 180

board = [[0] * 9 for _ in range(9)]
turn = 1
active_sub = -1
game_over = False
meta = [0] * 9
depth = 5
profile = "Balanced"
nodes_searched = 0
win_prob = 50

font_large = pygame.font.SysFont("consolas", 28, bold=True)
font_med = pygame.font.SysFont("consolas", 18)
font_small = pygame.font.SysFont("consolas", 14)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if not game_over and BOARD_LEFT <= mx <= BOARD_LEFT + BOARD_SIZE and BOARD_TOP <= my <= BOARD_TOP + BOARD_SIZE:
                cell_col = (mx - BOARD_LEFT) // CELL_SIZE
                cell_row = (my - BOARD_TOP) // CELL_SIZE
                sub_row = cell_row // 3
                sub_col = cell_col // 3
                sub = sub_row * 3 + sub_col
                local_row = cell_row % 3
                local_col = cell_col % 3
                local = local_row * 3 + local_col
                turn, active_sub, winner = make_move(board,meta, sub, local, turn, active_sub)
                if winner != 0:
                    game_over = True
                elif turn == -1 and not game_over:
                    moves_played = sum(1 for s in range(9) for c in range(9) if board[s][c] != 0)
                    ai_depth = 3 if moves_played<10 else 4 if moves_played<25 else 5
                    ai_move = get_best_move(board,meta,active_sub,ai_depth)
                    if ai_move:
                        turn, active_sub, winner = make_move(board, meta, ai_move[0], ai_move[1],turn, active_sub)
                        if winner != 0:
                            game_over = True


            if 600 <= mx <= 650 and 480 <= my <= 510:
                depth = 4
            if 660 <= mx <= 710 and 480 <= my <= 510:
                depth = 5
            if 720 <= mx <= 770 and 480 <= my <= 510:
                depth = 6
            if 600 <= mx <= 710 and 540 <= my <= 570:
                profile = "Aggressive"
            if 720 <= mx <= 840 and 540 <= my <= 570:
                profile = "Balanced"


    screen.fill((10, 12, 20))
    if active_sub != -1:
        row = active_sub // 3
        col = active_sub % 3
        ax = BOARD_LEFT + col * SUB_SIZE
        ay = BOARD_TOP + row * SUB_SIZE
        pygame.draw.rect(screen, (20, 50, 30), (ax, ay, SUB_SIZE, SUB_SIZE))

    for s in range(9):
        sr = s // 3
        sc = s % 3
        sx = BOARD_LEFT + sc * SUB_SIZE
        sy = BOARD_TOP + sr * SUB_SIZE
        for c in range(9):
            if board[s][c] == 1:
                cr = c // 3
                cc = c % 3
                cx = sx + cc * CELL_SIZE + CELL_SIZE // 2
                cy = sy + cr * CELL_SIZE + CELL_SIZE // 2
                o = 18
                pygame.draw.line(screen, (80, 160, 255), (cx - o, cy - o), (cx + o, cy + o), 3)
                pygame.draw.line(screen, (80, 160, 255), (cx + o, cy - o), (cx - o, cy + o), 3)
            elif board[s][c] == -1:
                cr = c // 3
                cc = c % 3
                cx = sx + cc * CELL_SIZE + CELL_SIZE // 2
                cy = sy + cr * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(screen, (255, 90, 80), (cx, cy), 18, 3)
        if meta[s] != 0:  # ← same level as "for c", not inside it
            cx = BOARD_LEFT + sc * SUB_SIZE + SUB_SIZE // 2
            cy = BOARD_TOP + sr * SUB_SIZE + SUB_SIZE // 2
            if meta[s] == 1:
                pygame.draw.line(screen, (80, 160, 255), (cx - 60, cy - 60), (cx + 60, cy + 60), 8)
                pygame.draw.line(screen, (80, 160, 255), (cx + 60, cy - 60), (cx - 60, cy + 60), 8)
            else:
                pygame.draw.circle(screen, (255, 90, 80), (cx, cy), 70, 8)

    for i in range(1, 9):
        x = BOARD_LEFT + i * CELL_SIZE
        y = BOARD_TOP + i * CELL_SIZE
        if i % 3 == 0:
            pygame.draw.line(screen, (70, 80, 120), (x, BOARD_TOP), (x, BOARD_TOP + BOARD_SIZE), 4)
            pygame.draw.line(screen, (70, 80, 120), (BOARD_LEFT, y), (BOARD_LEFT + BOARD_SIZE, y), 4)
        else:
            pygame.draw.line(screen, (35, 40, 60), (x, BOARD_TOP), (x, BOARD_TOP + BOARD_SIZE), 1)
            pygame.draw.line(screen, (35, 40, 60), (BOARD_LEFT, y), (BOARD_LEFT + BOARD_SIZE, y), 1)

    pygame.draw.rect(screen, (70, 80, 120), (BOARD_LEFT, BOARD_TOP, BOARD_SIZE, BOARD_SIZE), 2)

    title = font_large.render("UltiMind", True, (60, 200, 100))
    screen.blit(title, (BOARD_LEFT, 20))

    pygame.draw.rect(screen, (15, 18, 30), (580, 80, 370, 560), border_radius=8)
    pygame.draw.rect(screen, (35, 40, 60), (580, 80, 370, 560), 1, border_radius=8)

    if game_over:
        msg = "X WINS!" if winner == 1 else "O WINS!"
        color = (80, 160, 255) if winner == 1 else (255, 90, 80)
        overlay = pygame.Surface((300, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (BOARD_LEFT + 120, BOARD_TOP + 220))
        text = font_large.render(msg, True, color)
        screen.blit(text, (BOARD_LEFT + 160, BOARD_TOP + 240))

    pygame.display.flip()
    clock.tick(60)
