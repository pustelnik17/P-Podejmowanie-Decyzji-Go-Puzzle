import gurobipy as gp
import numpy as np
from gurobipy import GRB

N = 5
M = 2
T = 1 + 2

empty, black, white = 0, 1, 2

board = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 1, 0, 2],
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

# x[i,j,t] = 1 jeśli czarny stawia kamień na polu (i, j)-tym w turze t-tej lub jeżeli kamień czarny z tury t-1 pozostaje na planszy
x = model.addVars(N, N, T, vtype=GRB.BINARY)
# x[i,j,t] = 1 jeśli biały kamień pozostaje na polu (i, j)-tym w turze t-tej
y = model.addVars(N, N, T, vtype=GRB.BINARY)

# Białe znajdują się tam gdzie na planszy początkowej, chyba, że zostaną zbite
for i in range(N):
    for j in range(N):
        for t in range(T):
            model.addConstr(y[i, j, t] <= (1 if board[i, j] == white else 0))

# Ustawienie początkowe kamieni czarnych
for i in range(N):
    for j in range(N):
        model.addConstr(x[i, j, 0] == (1 if board[i, j] == black else 0))

# W każdej turze oprócz zerowej wykonać możemy tylko jeden ruch
for t in range(1, T):
    model.addConstr(gp.quicksum(x[i, j, t] for i in range(N) for j in range(N)) <= 1)

# Wykonany ruch nie może się powtórzyć
for i in range(N):
    for j in range(N):
        model.addConstr(gp.quicksum(x[i, j, t] for t in range(T)) <= 1)

# TODO Zbijanie grupy białych kamieni jeśli żaden z elementów składającyh się na grupę nie będą miały oddechu
# TODO Zapobieganie ruchu w turze, który sprawia, że położenie czarnego kamienia sprawia, że zbita zostaje grupa kamieni czarnych (traci oddech) - wyjątek: jeśli czarny kamień zagraża grupie czarncyh, ale położenie go zbija grupę białych i tworzy się nowy oddech dla zagrożonej grupy czarnych

# Funkcja celu
model.setObjective(
    gp.quicksum(x[i, j, t] for i in range(N) for j in range(N) for t in range(T)) + 
    gp.quicksum(y[i, j, t] for i in range(N) for j in range(N) for t in range(T)),
    GRB.MAXIMIZE
)

model.optimize()

if model.status == gp.GRB.OPTIMAL:
    print("\nWynikowa plansza:", model.ObjVal)
    for i in range(N):
        row = ""
        for j in range(N):
            if board[i, j] == black:
                row += "● "  # czarny
            elif board[i, j] == white:
                row += "○ "  # biały
            else:
                row += ". "  # puste     
        row += "       "
        for j in range(N):
            if max(x[i, j, t].X for t in range(T)) > 0.5:
                row += "● "  # czarny
            elif max(y[i, j, t].X for t in range(T)) > 0.5:
                row += "○ "  # biały
            else:
                row += ". "  # puste
        print(row)
