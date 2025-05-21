import gurobipy as gp
import numpy as np
from gurobipy import GRB

N = 5
T = 1

empty, black, white = 0, 1, 2

board = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 1, 0, 2],
    [1, 2, 2, 1, 0],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0]
])
# board = np.array([
#     [2, 2, 2, 2, 2],
#     [2, 1, 1, 2, 2],
#     [2, 2, 2, 2, 2],
#     [2, 2, 2, 2, 2],
#     [2, 2, 2, 2, 0]
# ])

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
# x[i,j,t] = 1 jeśli czarny stawia kamień na polu (i, j)-tym w turze t-tej lub jeżeli kamień czarny z tury t-1 pozostaje na planszy
xl = model.addVars(N, N, T, vtype=GRB.BINARY)
# x[i,j,t] = 1 jeśli biały kamień pozostaje na polu (i, j)-tym w turze t-tej
yl = model.addVars(N, N, T, vtype=GRB.BINARY)


# Ustawienie początkowe kamieni czarnych
for i in range(N):
    for j in range(N):
        model.addConstr(x[i, j, 0] == (1 if board[i, j] == black else 0))

# Ustawienie początkowe kamieni białych
for i in range(N):
    for j in range(N):
        model.addConstr(y[i, j, 0] == (1 if board[i, j] == white else 0))

# Białe nie mogą być w miejscu gdzie ich wcześniej nie było
for i in range(N):
    for j in range(N):
        for t in range(1, T):
            model.addConstr(y[i, j, t] <= y[i, j, t-1])

# Czarne nie mogą zostać podniesione
for i in range(N):
    for j in range(N):
        for t in range(1, T):
            model.addConstr(x[i, j, t] >= x[i, j, t-1])

# Na danym polu nie może naraz znajdować się biały i czarny kamień
for i in range(N):
    for j in range(N):
        for t in range(T):
            model.addConstr(x[i, j, t] + y[i, j, t] <= 1)

# W każdej turze oprócz zerowej wyłożyć możemy tylko jeden dodatkowy kamień czarny
for t in range(1, T):
    model.addConstr(gp.quicksum(x[i, j, t] - x[i, j, t-1] for i in range(N) for j in range(N)) <= 1)

# Oddechy białego w turze t-tej
for i in range(N):
    for j in range(N):
        for t in range(T):
            # Białe kamienie z oddechami mogą być tylko tam, gdzie są białe kamienie
            model.addConstr(yl[i, j, t] <= y[i, j, t])
            # Jeśli conajmniej 1 sąsiednie pole jest puste, to kamień ma oddech 
            # model.addConstr(yl[i, j, t] <= gp.quicksum((1-x[ni, nj, t])*(1-y[ni, nj, t]) for ni, nj in neighbors(i, j)))
            # Jeśli na conajmniej 1 sąsiednim polu jest biały kamień, który ma oddech, to kamień ma oddech 
            model.addConstr(yl[i, j, t] <= gp.quicksum(yl[ni, nj, t] for ni, nj in neighbors(i, j)))   

# Funkcja celu - maksymalizujemy ilość kamieni na planszy
model.setObjective(
    gp.quicksum(x[i, j, t] for i in range(N) for j in range(N) for t in range(T)) * N*N + 
    gp.quicksum(y[i, j, t] for i in range(N) for j in range(N) for t in range(T)) * N*N +
    gp.quicksum(yl[i, j, t] for i in range(N) for j in range(N) for t in range(T)),
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
            if x[i, j, T-1].X > 0.5:
                row += "● "  # czarny
            elif y[i, j, T-1].X > 0.5:
                row += "○ "  # biały
            else:
                row += ". "  # puste
        print(row)

    # for t in range(T):
    #     for i in range(N):
    #         for j in range(N):
    #             print(round(z[i, j, t].X), end=" ")
    #         print()
    #     print()
    # print()
    for t in range(T):
        for i in range(N):
            for j in range(N):
                print(round(yl[i, j, t].X), end=" ")
            print()
        print()
    print()
    
    # for t in range(T):
    #     for i in range(N):
    #         for j in range(N):
    #             print(round(sum((1-x[ni, nj, t].X)*(1-y[ni, nj, t].X) + yl[ni, nj, t].X for ni, nj in neighbors(i, j))), end=" ")
    #         print()
    #     print()
    # print()
