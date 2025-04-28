import gurobipy as gp
from gurobipy import GRB

N = 5
M = 2
empty, black, white = 0, 1, 2

# Plansza początkowa: 0 = puste, 1 = czarny, 2 = biały
board = [
    [2, 0, 0, 0, 0],
    [2, 2, 2, 0, 0],
    [2, 2, 0, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

# Sąsiedzi: góra, dół, lewo, prawo
def neighbors(i, j):
    return [(i+di, j+dj) for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]
            if 0 <= i+di < N and 0 <= j+dj < N]

model = gp.Model("go_advanced")
model.setParam("OutputFlag", 0) 

# x[i,j] = 1 jeśli czarny stawia kamień
x = model.addVars(N, N, vtype=GRB.BINARY)

# y[i,j] = 1 jeśli biały zostaje zbity
y = model.addVars(N, N, vtype=GRB.BINARY)

# t[i,j] = 1 jeśli puste pole jest otoczone przez czarne
t = model.addVars(N, N, vtype=GRB.BINARY)

# Ilość kamieni czarnych: nie możemy wyłożyć więcej kamieni czarnych niż posiadamy
model.addConstr(gp.quicksum(x[i, j] for i in range(N) for j in range(N)) <= M)

# Nie można stawiać kamienia na zajętym polu
for i in range(N):
    for j in range(N):
        if board[i][j] != empty:
            model.addConstr(x[i, j] == 0)

# TODO: Zakaz samobójstw: jeśli czarny kamień nie ma sąsiedniego oddechu ani nie zbija białych, nie może tam stać

# Zbijanie: biały kamień może zostać zbity, jeśli wokół niego będą same czarne
for i in range(N):
    for j in range(N):
        if board[i][j] == white:
            model.addConstr(y[i, j] <= gp.quicksum(x[ni, nj] for ni, nj in neighbors(i, j)))

# TODO: Terytorium: pole musi być puste i otoczone przez czarne

# Funkcja celu: maksymalizujemy sumę kamieni TODO: + zdobyte terytorium + zbite białe
model.setObjective(
    gp.quicksum(x[i, j] for i in range(N) for j in range(N)),
    GRB.MAXIMIZE
)

model.optimize()

print("\nWynikowa plansza:")
for i in range(N):
    row = ""
    for j in range(N):
        if x[i, j].X > 0.5:
            row += "● "  # czarny
        elif board[i][j] == white and y[i, j].X < 0.5:
            row += "○ "  # biały
        else:
            row += ". "  # puste
    print(row)


total_score = model.ObjVal
print(f"\nPunkty Gracza 1: {int(total_score)}")