PEN_LOCS = set()
PEN = set([(1, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 1)])

f = open("storing_info1", "r")
rawStates = f.readlines()

rawStates = [i.strip().replace("(", "").replace(")", "").replace(
    ",", "").split(" ") for i in rawStates]
states = {((int(i[0]), int(i[1])), (int(i[2]), int(i[3]))): float(i[4]) for i in rawStates}
# this processes the stored states


def onGrid(grid, x, y):
    # tells us if a position is valid.
    return x >= 0 and x < len(grid) and y >= 0 and y < len(grid) and (x, y) not in PEN_LOCS

# getting a grid based on the size in order to make it easy to validate states


def getGrid(size: int):
    center: int = int(size/2)
    if size < 5:
        size = 5
    if size % 2 == 0:
        size += 1
    grid = [[False for i in range(size)]
            for j in range(size)]
    for i in PEN:
        grid[i[0] + center][i[1] + center] = True
        PEN_LOCS.add((i[0] + center, i[1] + center))
    return grid


grid = getGrid(25)

expectedMinimumTForGivenSheepPos = 0
numberOfSheepPos = 0
for i in range(25):
    for j in range(25):
        numberOfSheepPos += 1
        min = (0, 0)
        if onGrid(grid, i, j):
            for state in states:
                if state[1] == (i, j):
                    if states[state] < states[(min, (i, j))]:
                        min = state[0]
            expectedMinimumTForGivenSheepPos += states[(min, (i, j))]
# this will get the expected minimum T value for a random valid sheep position
print(expectedMinimumTForGivenSheepPos/numberOfSheepPos)
