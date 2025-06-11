import numpy as np
import random
import copy

N = 9  # rozmiar planszy, np. 9x9
T = 9  # liczba czarnych tur

# Przyklad początkowej planszy
# 0 = puste, 1 = czarne, 2 = białe
initial_board = np.zeros((N, N), dtype=int)

initial_board[2][2] = 2
initial_board[4][4] = 1
initial_board[4][6] = 1
initial_board[4][5] = 2
initial_board[1][4] = 1
initial_board[8][1] = 2
initial_board[8][2] = 1






#Funkcja sprawdzająca czy pole ma oddech
def has_liberty(board, x, y, visited=None):
    if visited is None:
        visited = set()
    if (x, y) in visited:
        return False
    visited.add((x, y))
    color = board[x, y]
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
            if board[nx, ny] == 0:
                return True
            if board[nx, ny] == color and has_liberty(board, nx, ny, visited):
                return True
    return False


#Funkcja do usuwania martwych (otoczonych ) kamieni
def remove_dead_stones(board, color):
    board = board.copy()
    visited = set()
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x, y] == color and (x, y) not in visited:
                group = []
                stack = [(x, y)]
                has_lib = False
                while stack:
                    i, j = stack.pop()
                    if (i, j) in visited:
                        continue
                    visited.add((i, j))
                    group.append((i, j))
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < board.shape[0] and 0 <= nj < board.shape[1]:
                            if board[ni, nj] == 0:
                                has_lib = True
                            elif board[ni, nj] == color:
                                stack.append((ni, nj))
                if not has_lib:
                    for i, j in group:
                        board[i, j] = 0
    return board


def apply_moves(board, moves):
    new_board = board.copy()
    for (x, y) in moves:
        if new_board[x, y] != 0:
            return None  # nielegalny ruch
        new_board[x, y] = 1
        new_board = remove_dead_stones(new_board, 2)  # usuwamy zbite białe
        new_board = remove_dead_stones(new_board, 1)  # unikamy samobójstw
    return new_board


def count_white_captures(before, after):
    return np.sum(before == 2) - np.sum(after == 2)


def objective(board_before, moves):
    board_after = apply_moves(board_before, moves)
    if board_after is None:
        return -1e9  # kara za nielegalne ruchy
    captures = count_white_captures(board_before, board_after)
    return captures + len(moves)


def generate_neighbor(moves, board_shape, board):
    new_moves = moves.copy()
    idx = random.randint(0, len(moves) - 1)
    for _ in range(100):
        x, y = random.randint(0, board_shape[0]-1), random.randint(0, board_shape[1]-1)
        if board[x, y] == 0 and (x, y) not in new_moves:
            new_moves[idx] = (x, y)
            break
    return new_moves


#temperatura początkowa odpowiednia to n*n*T gdzie n to długość planszy - bierzemy taką temperaturę dlatego że na początku umożliwia akceptację pierwszgo rozwiązania

def simulated_annealing(board, T, iterations=10000, temp_start=N ** 2 , temp_end=0.01,
                        cooling_schedule='logarithmic', alpha=0.7):

    empty = list(zip(*np.where(board == 0)))
    if len(empty) < T:
        print("Błąd: Za mało pustych pól na planszy, aby postawić T kamieni.")
        return [], -1

    current = random.sample(empty, T)
    best = current
    best_score = objective(board, best)
    temp = temp_start

    
    if cooling_schedule == 'linear':
        temp_decrement = (temp_start - temp_end) / iterations

    for it in range(iterations):
        neighbor = generate_neighbor(current, board.shape, board)
        score_curr = objective(board, current)
        score_neigh = objective(board, neighbor)
        delta = score_neigh - score_curr

        if delta > 0 or (temp > 0 and random.random() < np.exp(delta / temp)):
            current = neighbor
            if score_neigh > best_score:
                best_score = score_neigh
                best = neighbor


        if cooling_schedule == 'geometric':
            temp *= alpha
        elif cooling_schedule == 'logarithmic':
            temp = temp_start * (temp_end / temp_start) ** (it / iterations)
        elif cooling_schedule == 'linear':
            temp -= temp_decrement
        else:
            raise ValueError(f"Nieznany schemat chłodzenia: {cooling_schedule}")

        # Zabezpieczenie, żeby temperatura nie spadła poniżej zera
        if temp < 0:
            temp = 0

    return best, best_score

def print_board(board, black_moves=[]):
    display = ""
    for i in range(board.shape[0]):
        row = ""
        for j in range(board.shape[1]):

            if (i, j) in black_moves:
                row += "● "

            elif board[i, j] == 1:
                row += "● "
            elif board[i, j] == 2:
                row += "○ "
            else:
                row += ". "
        display += row + "\n"
    print(display)



print_board(initial_board)
best_moves, best_score = simulated_annealing(initial_board, T)
print("Najlepszy wynik:", best_score)
print("Ruchy:")
print("\nWynikowa plansza:")
final_board = apply_moves(initial_board, best_moves)
print_board(final_board, best_moves)

