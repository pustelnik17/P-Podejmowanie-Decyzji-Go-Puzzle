import gurobipy as gp
import numpy as np
from gurobipy import GRB

N = 5
M = 6
empty, black, white = 0, 1, 2

board = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2],
    [0, 2, 2, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]) 

# Sąsiedzi: góra, dół, lewo, prawo
def neighbors(i, j):
    return [(i+di, j+dj) for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]
            if 0 <= i+di < N and 0 <= j+dj < N]

model = gp.Model("go")
model.setParam("OutputFlag", 0) 

# x[i,j] = 1 jeśli czarny stawia kamień na polu i, j
x = model.addVars(N, N, vtype=GRB.BINARY)

# y_l[i,j] = 1 jeśli biały kamień posiada oddech lub pole jest puste
y_l = model.addVars(N, N, vtype=GRB.BINARY)

# Ilość kamieni czarnych: nie możemy wyłożyć więcej kamieni czarnych niż posiadamy
model.addConstr(gp.quicksum(x[i, j] for i in range(N) for j in range(N)) <= M)

# Kamnienie czarne, które zostały położone na planszy przed rozpoczeńciem
for i in range(N):
    for j in range(N):
        if board[i][j] == black:
            model.addConstr(x[i, j] == 1)

# Nie można stawiać kamienia na zajętym polu chyba, że kamień został zbity
for i in range(N):
    for j in range(N):
        if board[i][j] == white:
            model.addConstr(x[i, j] <= 1 - y_l[i, j])

# TODO: Zakaz samobójstw: czarny kamień musi mieć oddech


# Wykrywanie oddechów białych kamieni
for i in range(N):
    for j in range(N):
        if board[i, j] == empty:
            model.addConstr(y_l[i, j] == 1-x[i, j])
        if board[i, j] == white:
            model.addConstr(y_l[i, j] == gp.max_(y_l[ni, nj] for ni, nj in neighbors(i, j)))


# Funkcja celu: maksymalizujemy sumę kamieni + zbite białe TODO: + zdobyte terytorium 
model.setObjective(
    gp.quicksum(x[i, j] for i in range(N) for j in range(N)) +  
    gp.quicksum(1 - y_l[i, j] for i in range(N) for j in range(N)),
    GRB.MAXIMIZE
)

model.optimize()

if gp.GRB.OPTIMAL:
    print("\nWynikowa plansza:")
    for i in range(N):
        row = ""
        for j in range(N):
            if x[i, j].X > 0.5:
                row += "● "  # czarny
            elif board[i][j] == white and 1 - y_l[i, j].X < 0.5:
                row += "○ "  # biały
            else:
                row += ". "  # puste
        print(row)

    total_score = model.ObjVal
    print(f"\nPunkty Gracza 1: {int(total_score)}")
