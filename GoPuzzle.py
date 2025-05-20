import gurobipy as gp
import numpy as np
from gurobipy import GRB

N = 5
M = 1
empty, black, white = 0, 1, 2

board = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 0, 0, 2],
    [0, 2, 2, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]) 
board = np.array([
    [2, 2, 2, 2, 2],
    [2, 0, 2, 2, 2],
    [2, 0, 2, 0, 2],
    [2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2]
])

# Sąsiedzi: góra, dół, lewo, prawo
def neighbors(i, j):
    return [(i+di, j+dj) for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]
            if 0 <= i+di < N and 0 <= j+dj < N]

model = gp.Model("go")
model.setParam("OutputFlag", 0) 

# x[i,j] = 1 jeśli czarny stawia kamień na polu i, j
x = model.addVars(N, N, vtype=GRB.BINARY)
# x[i,j] = 1 jeśli biały stawia kamień na polu i, j
y = model.addVars(N, N, vtype=GRB.BINARY)
# x_l[i,j] = 1 jeśli czarny kamień posiada oddech lub pole jest puste
x_l = model.addVars(N, N, vtype=GRB.BINARY)
# y_l[i,j] = 1 jeśli biały kamień posiada oddech lub pole jest puste
y_l = model.addVars(N, N, vtype=GRB.BINARY)

# Ilość kamieni czarnych: nie możemy wyłożyć więcej kamieni czarnych niż posiadamy
model.addConstr(gp.quicksum(x[i, j] for i in range(N) for j in range(N)) <= M)

# Kamnienie czarne, które zostały położone na planszy przed rozpoczeńciem
for i in range(N):
    for j in range(N):
        if board[i][j] == black:
            model.addConstr(x[i, j] == 1)

for i in range(N):
    for j in range(N):
        if board[i][j] == white:
            model.addConstr(y[i, j] <= y_l[i, j])
        else:
            model.addConstr(y[i, j] == 0)

# Nie można stawiać kamienia na zajętym polu chyba, że kamień został zbity
for i in range(N):
    for j in range(N):
        if board[i][j] == white:
            model.addConstr(x[i, j] <= 1 - y_l[i, j])

# Czarny kamień musi mieć oddech
# for i in range(N):
#     for j in range(N):
#         if board[i, j] == white:
#             model.addConstr(x_l[i, j] == 1-y[i, j])
#         else:
#             model.addConstr(x_l[i, j] == gp.max_(x_l[ni, nj] for ni, nj in neighbors(i, j)))
for i in range(N):
    for j in range(N):
        if board[i, j] == empty:
            model.addConstr(x_l[i, j] <= 1-y[i, j])
            model.addConstr(x_l[i, j] <= 1-x[i, j])
        if board[i, j] == black:
            model.addConstr(x_l[i, j] == gp.max_(x_l[ni, nj] for ni, nj in neighbors(i, j)))

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
    gp.quicksum(1 - y_l[i, j] for i in range(N) for j in range(N)) * N*N +
    gp.quicksum(x_l[i, j] for i in range(N) for j in range(N)) +
    gp.quicksum(y[i, j] for i in range(N) for j in range(N)),
    GRB.MAXIMIZE
)

model.optimize()

if model.status == gp.GRB.OPTIMAL:
    print("\nWynikowa plansza:")
    for i in range(N):
        row = ""
        for j in range(N):
            if x[i, j].X > 0.5:
                row += "● "  # czarny
            elif y[i, j].X > 0.5:
                row += "○ "  # biały
            else:
                row += ". "  # puste
        row += "       "
        for j in range(N):
            if board[i, j] == black:
                row += "● "  # czarny
            elif board[i, j] == white:
                row += "○ "  # biały
            else:
                row += ". "  # puste     
        print(row)

    total_score = model.ObjVal
    print(f"\nPunkty Gracza 1: {int(total_score)}")

    for i in range(N):
        print()
        for j in range(N):
            print(round(x[i, j].X), end=" ")
    print()

    for i in range(N):
        print()
        for j in range(N):
            print(round(y_l[i, j].X), end=" ")
    print()

    for i in range(N):
        print()
        for j in range(N):
            print(round(x_l[i, j].X), end=" ")
    print()
    
    for i in range(N):
        print()
        for j in range(N):
            print(round(y[i, j].X), end=" ")
    print()