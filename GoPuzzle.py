import gurobipy as gp
import numpy as np
from gurobipy import GRB

N = 5
M = 8
empty, black, white = 0, 1, 2

# Plansza początkowa: 0 = puste, 1 = czarny, 2 = biały
# board = [
#     [0,0,1],
#     [1,0,0],
#     [1,1,0]
# ]
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

# x[i,j] = 1 jeśli czarny stawia kamień
x = model.addVars(N, N, vtype=GRB.BINARY)

# y[i,j] = 1 jeśli biały zostaje zbity
y = model.addVars(N, N, vtype=GRB.BINARY)

def boundary():
    def DFS(node: tuple[int, int]):
        def _DFS(node: tuple[int, int], group: list[tuple[int, int]], target: list[int], outerRing: list[tuple[int, int]]):
            unvisitedNodes.remove(node)
            group.append(node)
            for neighbour in neighbors(*node):
                if neighbour in unvisitedNodes:
                    if board[neighbour[0]][neighbour[1]] in target:
                        _DFS(neighbour, group, target, outerRing)
                    else:
                        outerRing.append(board[neighbour[0]][neighbour[1]])

            return group, outerRing

        return _DFS(node, [], [board[node[0]][node[1]]], [])
    
    unvisitedNodes = [(i, j) for i in range(N) for j in range(N)]
    while len(unvisitedNodes) > 0:
        print(DFS(unvisitedNodes[0]))
        
    return 0
boundary()

# Ilość kamieni czarnych: nie możemy wyłożyć więcej kamieni czarnych niż posiadamy
model.addConstr(gp.quicksum(x[i, j] for i in range(N) for j in range(N)) <= M)

# Kamnienie, które zostały położone na planszy przed rozpoczeńciem
for i in range(N):
    for j in range(N):
        if board[i][j] == black:
            model.addConstr(x[i, j] == 1)

# Nie można stawiać kamienia na zajętym polu chyba, że kamień został zbity
for i in range(N):
    for j in range(N):
        if board[i][j] == white:
            model.addConstr(x[i, j] <= y[i, j])

# TODO: Zakaz samobójstw: czarny kamień musi mieć oddech


# Zbijanie: biały kamień może zostać zbity, jeśli wokół niego będą same czarne
for i in range(N):
    for j in range(N):
        if board[i][j] == white:
            for ni, nj in neighbors(i, j):
                model.addConstr(y[i, j] <= x[ni, nj])
        else:
            model.addConstr(y[i, j] == 0)

# Funkcja celu: maksymalizujemy sumę kamieni + zbite białe TODO: + zdobyte terytorium 
model.setObjective(
    gp.quicksum(x[i, j] for i in range(N) for j in range(N)) + 
    gp.quicksum(y[i, j] for i in range(N) for j in range(N)) * 2 +
    boundary(),
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
            elif board[i][j] == white and y[i, j].X < 0.5:
                row += "○ "  # biały
            else:
                row += ". "  # puste
        print(row)

    total_score = model.ObjVal
    print(f"\nPunkty Gracza 1: {int(total_score)}")

    # print("Wartości zmiennej x jako macierzy:")
    # for i in range(N):
    #     row = ""
    #     for j in range(N):
    #         val = int(y[i, j].X + 0.5)  # zaokrąglenie do 0/1
    #         row += f"{val} "
    #     print(row)

    # print("Wartości zmiennej x jako macierzy:")
    # for i in range(N):
    #     row = ""
    #     for j in range(N):
    #         val = int(x[i, j].X + 0.5)  # zaokrąglenie do 0/1
    #         row += f"{val} "
    #     print(row)