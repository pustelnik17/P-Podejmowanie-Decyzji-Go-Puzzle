import gurobipy as gp
import numpy as np
from gurobipy import GRB


N = 5
T = 5

board = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2],
    [1, 2, 2, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0]
])

N = 4
T = 5
board = np.array([
    [1, 1, 1, 2],
    [1, 1, 1, 0],
    [1, 1, 0, 1],
    [0, 1, 1, 0],
])

N = 4
T = 4
board = np.array([
    [2, 2, 2, 2],
    [2, 2, 0, 0],
    [2, 2, 2, 2],
    [2, 2, 2, 2],
])

N = 3
T = 5
board = np.array([
    [1, 1, 1],
    [0, 2, 0],
    [0, 1, 1],
])

N = 3
T = 5
board = np.array([
    [2, 2, 2],
    [2, 0, 2],
    [2, 0, 2],
])

# Indeksy sąsiadów pola (i, j)-ego
def neighbors(i, j):
    return [(i+di, j+dj) for di, dj in [(-1,0),(1,0),(0,-1),(0,1)] if 0 <= i+di < N and 0 <= j+dj < N]

model = gp.Model("Go Puzzle")
model.setParam("OutputFlag", 0) 

# N - bok planszy

# T - ilość tur
# t=0 - początkowe ustawienie planszy (bez stawianego kamienia), t=T-1 - końcowe ustawienie planszy (bez stawianego kamienia)

# x[i,j,t] = 1 jeśli czarny stawia kamień na polu (i, j)-tym w turze t-tej lub jeżeli kamień czarny z tury t-1 pozostaje na planszy
x = model.addVars(N, N, T, vtype=GRB.BINARY)
# y[i,j,t] = 1 jeśli biały kamień pozostaje na polu (i, j)-tym w turze t-tej
y = model.addVars(N, N, T, vtype=GRB.BINARY)
# xl[i,j,t] = 1 jeśli czarny ma oddech na polu (i, j)-tym po turze t-1-tej
xl = model.addVars(N, N, T, vtype=GRB.BINARY)
# yl[i,j,t] = 1 jeśli biały ma oddech na polu (i, j)-tym po turze t-1-tej
yl = model.addVars(N, N, T, vtype=GRB.BINARY)


# Ustawienie początkowe kamieni czarnych
for i in range(N):
    for j in range(N):
        model.addConstr(x[i, j, 0] == (1 if board[i, j] == 1 else 0))

# Ustawienie początkowe kamieni białych
for i in range(N):
    for j in range(N):
        model.addConstr(y[i, j, 0] == (1 if board[i, j] == 2 else 0))

# Białe nie mogą być w miejscu gdzie tracą oddech
for i in range(N):
    for j in range(N):
        for t in range(1, T):
            model.addConstr(y[i, j, t] == y[i, j , t-1] * yl[i, j, t-1])

# Czarne wystawić możemy tylko na polach, gdzie będą mieć oddech
for i in range(N):
    for j in range(N):
        for t in range(1, T):
            model.addConstr(x[i, j, t] <= xl[i, j, t-1])

# Czarne nie mogą zostać podniesione
for i in range(N):
    for j in range(N):
        for t in range(1, T):
            model.addConstr(x[i, j, t] >= x[i, j, t-1])

# Na polu może znajdować się tylko jeden kolor kamienia naraz
for i in range(N):
    for j in range(N):
        for t in range(T):
            model.addConstr(y[i, j, t] + x[i, j, t] <= 1)

# W każdej turze oprócz zerowej wyłożyć możemy tylko jeden dodatkowy kamień czarny
for t in range(1, T):
    model.addConstr(gp.quicksum(x[i, j, t] for i in range(N) for j in range(N))- gp.quicksum(x[i, j, t-1] for i in range(N) for j in range(N)) <= 1)

# W Ostatniej turze nie wykładamy żadnego kamienia
model.addConstr(gp.quicksum(x[i, j, T-1] for i in range(N) for j in range(N)) - gp.quicksum(x[i, j, T-2] for i in range(N) for j in range(N)) == 0)

# Biały ma oddech na polu (i, j)-ym jeśli jest ono puste, lub jeżeli znajdujący się tam kamień biały jest częścią stringu sąsiadującym z polem pustym
for i in range(N):
    for j in range(N):
        for t in range(T):
            isEmpty = model.addVar(vtype=GRB.BINARY)
            model.addConstr(isEmpty == (1 - y[i, j, t]) * (1 - x[i, j, t]))

            inLibertedString = model.addVar(vtype=GRB.BINARY)
            maxVar = model.addVar(vtype=GRB.BINARY)
            model.addConstr(maxVar == gp.max_(yl[ni, nj, t] for ni, nj in neighbors(i, j)))
            model.addGenConstrAnd(inLibertedString, [maxVar, y[i, j, t]])
            
            model.addGenConstrOr(yl[i, j , t], [isEmpty, inLibertedString])

# Czarny ma oddech na polu (i, j)-ym jeśli jest ono puste, lub jeżeli znajdujący się tam kamień czarny jest częścią stringu sąsiadującym z polem pustym
for i in range(N):
    for j in range(N):
        for t in range(T):
            isEmpty = model.addVar(vtype=GRB.BINARY)
            model.addConstr(isEmpty == (1 - y[i, j, t]) * (1 - x[i, j, t]))

            inLibertedString = model.addVar(vtype=GRB.BINARY)
            maxVar = model.addVar(vtype=GRB.BINARY)
            model.addConstr(maxVar == gp.max_(xl[ni, nj, t] for ni, nj in neighbors(i, j)))
            model.addGenConstrAnd(inLibertedString, [maxVar, x[i, j, t]])
            
            model.addGenConstrOr(xl[i, j , t], [isEmpty, inLibertedString])

# Punkty liczone są z ilości wystawionych kamieni czarnych oraz ilości zbitych kamieni białych
model.setObjective(
    gp.quicksum(x[i, j, T-1] for i in range(N) for j in range(N))
    + gp.quicksum(y[i, j, 0] for i in range(N) for j in range(N))
    - gp.quicksum(y[i, j, T-1] for i in range(N) for j in range(N)),
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
                    row += "○ "  # czarny
                elif y[i, j, t].X > 0.5:
                    row += "● "  # biały
                else:
                    row += ". "  # puste
            row += "    "
        print(row)
    print()
    # for i in range(N):
    #     row = "" 
    #     for t in range(T):  
    #         for j in range(N):
    #             row += f"{round(yl[i, j, t].X)} "
    #         row += "    "
    #     print(row)
    # print()
    # for i in range(N):
    #     row = "" 
    #     for t in range(T):  
    #         for j in range(N):
    #             row += f"{round(y[i, j, t].X)} "
    #         row += "    "
    #     print(row)
    # print()
    # for i in range(N):
    #     row = "" 
    #     for t in range(T):  
    #         for j in range(N):
    #             row += f"{round(x[i, j, t].X)} "
    #         row += "    "
    #     print(row)
    # print()
    # for i in range(N):
    #     row = "" 
    #     for t in range(T):  
    #         for j in range(N):
    #             row += f"{round(xl[i, j, t].X)} "
    #         row += "    "
    #     print(row)
    # print()