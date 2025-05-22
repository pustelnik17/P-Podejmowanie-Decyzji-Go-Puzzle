import gurobipy as gp
import numpy as np
from gurobipy import GRB

N = 5
T = 7

empty, black, white = 0, 1, 2

board = [
    [1, 1, 1, 1, 0],
    [1, 2, 2, 0, 2],
    [1, 2, 0, 2, 1],
    [1, 2, 2, 1, 1],
    [1, 1, 1, 1, 1]
]

# N = 4
# T = 3
# board = [
#     [1, 1, 1, 2],
#     [1, 1, 1, 0],
#     [1, 1, 2, 1],
#     [2, 1, 1, 2],
# ]

# N = 3
# T = 5
# board = [
#     [1, 1, 1],
#     [0, 2, 0],
#     [0, 1, 1],
# ]

boardWhite = np.array(board)
boardBlack = np.array(board)
for i in range(N):
    for j in range(N):
        boardWhite[i, j] = 1 if boardWhite[i, j] == white else 0
        boardBlack[i, j] = 1 if boardBlack[i, j] == black else 0

# Sąsiedzi: góra, dół, lewo, prawo
def neighbors(i, j):
    return [(i+di, j+dj) for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]
            if 0 <= i+di < N and 0 <= j+dj < N]

model = gp.Model("go")
model.setParam("OutputFlag", 0) 

# x[i,j,t] = 1 jeśli czarny stawia kamień na polu (i, j)-tym w turze t-tej lub jeżeli kamień czarny z tury t-1 pozostaje na planszy
x = model.addVars(N, N, T, vtype=GRB.BINARY)
# y[i,j,t] = 1 jeśli biały kamień pozostaje na polu (i, j)-tym w turze t-tej
# y = model.addVars(N, N, T, vtype=GRB.BINARY)
# xl[i,j,t] = 1 jeśli czarny stawia kamień na polu (i, j)-tym w turze t-tej lub jeżeli kamień czarny z tury t-1 pozostaje na planszy
xl = model.addVars(N, N, T, vtype=GRB.BINARY)
# yl[i,j,t] = 1 jeśli biały kamień pozostaje na polu (i, j)-tym w turze t-tej
yl = model.addVars(N, N, T, vtype=GRB.BINARY)


# Ustawienie początkowe kamieni czarnych
for i in range(N):
    for j in range(N):
        model.addConstr(x[i, j, 0] == (boardBlack[i, j]))

# Ustawienie początkowe kamieni białych
# for i in range(N):
#     for j in range(N):
#         model.addConstr(y[i, j, 0] == (boardWhite[i, j]))

# Białe nie mogą być w miejscu gdzie ich wcześniej nie było
# for i in range(N):
#     for j in range(N):
#         for t in range(1, T):
#             model.addConstr(y[i, j, t] <= y[i, j, t-1])

# Czarne nie mogą zostać podniesione
for i in range(N):
    for j in range(N):
        for t in range(1, T):
            model.addConstr(x[i, j, t] >= x[i, j, t-1])

# Na danym polu nie może naraz znajdować się biały i czarny kamień
for i in range(N):
    for j in range(N):
        for t in range(T):
            model.addConstr(x[i, j, t] + boardWhite[i, j] * yl[i, j, t] <= 1)

# W każdej turze oprócz zerowej wyłożyć możemy tylko jeden dodatkowy kamień czarny
for t in range(1, T):
    model.addConstr(gp.quicksum(x[i, j, t] - x[i, j, t-1] for i in range(N) for j in range(N)) <= 1)

for i in range(N):
    for j in range(N):
        for t in range(T):
            # Jeśli pole jest puste to ma oddech
            model.addConstr(yl[i, j, t] >= (1 - x[i, j, t]) * (1 - boardWhite[i, j]))

            # Biały kamień ma oddech, jeśli jeden z sąsiadów ma oddech
            max_var = model.addVar(vtype=GRB.BINARY)
            model.addConstr(max_var == gp.max_(yl[ni, nj, t] for ni, nj in neighbors(i, j)))
            model.addConstr(yl[i, j, t] >= max_var * boardWhite[i, j])

# for i in range(N):
#     for j in range(N):
#         for t in range(T):
#             # Jeśli pole jest puste to ma oddech
#             model.addConstr(xl[i, j, t] >= (1 - x[i, j, t]) * (1 - boardWhite[i, j]))

#             # Biały kamień ma oddech, jeśli jeden z sąsiadów ma oddech
#             max_var = model.addVar(vtype=GRB.BINARY)
#             model.addConstr(max_var == gp.max_(yl[ni, nj, t] for ni, nj in neighbors(i, j)))
#             model.addConstr(yl[i, j, t] >= max_var * boardWhite[i, j])



# Funkcja celu
model.setObjective(
    gp.quicksum(x[i, j, t] for i in range(N) for j in range(N) for t in range(T))
    - N*N * gp.quicksum(yl[i, j, t] for i in range(N) for j in range(N) for t in range(T))
    - N*N * gp.quicksum(yl[i, j, t] for i in range(N) for j in range(N) for t in range(T)),
    GRB.MAXIMIZE
)

model.optimize()

if model.status == gp.GRB.OPTIMAL:
    print("\nWynikowa plansza:", model.ObjVal)
    for i in range(N):
        row = "" 
        for t in range(T):  
            for j in range(N):
                if x[i, j, t].X > 0.5:
                    row += "● "  # czarny
                elif boardWhite[i, j] * yl[i, j, t].X> 0.5:
                    row += "○ "  # biały
                else:
                    row += ". "  # puste
            row += "    "
        print(row)
    print()
    for i in range(N):
        row = "" 
        for t in range(T):  
            for j in range(N):
                row += f"{round(yl[i, j, t].X)} "
            row += "    "
        print(row)
    print()
    