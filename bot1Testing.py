from random import Random

# quality of life variables for looping through actions
PEN = set([(1, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 1)])
ALL_DIR = [(1, 1), (1, -1), (1, 0), (0, 1),
           (0, -1), (-1, 1), (-1, 0), (-1, -1)]
PEN_LOCS = set()

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


# same as the simulation algorithm in the sheepBot1 file.
numSheepPenned: int = 0
numSheepToPen = 10000
grid = getGrid(25)


for i in range(numSheepToPen):

    state = ((Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)),
             (Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)))
    while (grid[state[0][0]][state[0][1]] or grid[state[1][0]][state[1][1]]):
        state = ((Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)),
                 (Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)))

    while (True):
        if (state[0] == state[1]):
            break
        if state[1] == (int((len(grid) - 1)/2), int((len(grid) - 1)/2)):
            numSheepPenned += 1
            break
        resultStates = [((state[0][0] + i[0], state[0][1] + i[1]), (state[1][0], state[1][1]))
                        for i in ALL_DIR if onGrid(grid, state[0][0] + i[0], state[0][1] + i[1])]

        minState = resultStates[0]

        for resultState in resultStates:
            if states[resultState] < states[minState]:
                minState = resultState

        state = minState

        possibleActionsOfSheep = []
        deltaY = state[0][0] - state[1][0]
        deltaX = state[0][1] - state[1][1]
        if abs(deltaX) <= 2 and abs(deltaY) <= 2:
            if deltaY >= 0 and onGrid(grid, state[1][0] + 1, state[1][1] + 0):
                possibleActionsOfSheep.append((1, 0))
            if deltaY <= 0 and onGrid(grid, state[1][0] - 1, state[1][1] + 0):
                possibleActionsOfSheep.append((-1, 0))
            if deltaX >= 0 and onGrid(grid, state[1][0] + 0, state[1][1] + 1):
                possibleActionsOfSheep.append((0, 1))
            if deltaX <= 0 and onGrid(grid, state[1][0] + 0, state[1][1] - 1):
                possibleActionsOfSheep.append((0, -1))
        else:
            if onGrid(grid, state[1][0] + 1, state[1][1] + 0):
                possibleActionsOfSheep.append((1, 0))
            if onGrid(grid, state[1][0] - 1, state[1][1] + 0):
                possibleActionsOfSheep.append((-1, 0))
            if onGrid(grid, state[1][0] + 0, state[1][1] + 1):
                possibleActionsOfSheep.append((0, 1))
            if onGrid(grid, state[1][0] + 0, state[1][1] - 1):
                possibleActionsOfSheep.append((0, -1))

        if len(possibleActionsOfSheep) == 0:
            break
        sheepChoice = Random().randint(0, len(possibleActionsOfSheep) - 1)

        state = (state[0], (state[1][0] + possibleActionsOfSheep[sheepChoice]
                            [0], state[1][1] + possibleActionsOfSheep[sheepChoice][1]))

print(numSheepPenned/numSheepToPen)
