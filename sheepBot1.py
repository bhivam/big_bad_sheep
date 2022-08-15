from random import Random, random
from math import inf
import time


# to track the blocked cells
PEN = set([(1, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 1)])
BETA = 0.8
PEN_LOCS = set()


def setupEnvironment(size: int):
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

    states: dict = {}
    # dog is first tuple, sheep is second tuple
    for i in range(size):
        for j in range(size):
            for k in range(size):
                for l in range(size):
                    if (i, j) not in PEN_LOCS and (k, l) not in PEN_LOCS:
                        initialTStart: int = abs(
                            i - k) + abs(j - l) + abs(k - center) + abs(l - center)
                        states[((i, j), (k, l))] = initialTStart
    states[((center+2, center), (center - 1, center - 1))] = 1
    states[((center-2, center), (center - 1, center - 1))] = 1
    states[((center+2, center+1), (center - 1, center - 1))] = 1
    states[((center-2, center+1), (center - 1, center - 1))] = 1
    # add in initial guesses for T*(state) = 1 and 0 for the edge cases near and inside the pen respectively
    calculateTStars(states, size, grid)

    return grid, states


def calculateTStars(states: dict, size: int, grid):
    numStates = len(states)
    lossBetweenRounds = 0
    while True:
        for i in states:
            newState = 0
            if i[1] == (int(size/2), int(size/2)):
                newState = 0
            elif i[1] == i[0]:
                newState = 999999999999999999
            else:
                newState = calculateTStar(i, size, grid, states)

            lossBetweenRounds += newState - states[i]
            states[i] = newState
        if (abs(lossBetweenRounds/numStates) < 0.01):
            break
        lossBetweenRounds = 0


def onGrid(grid, x, y):
    return x >= 0 and x < len(grid) and y >= 0 and y < len(grid) and (x, y) not in PEN_LOCS


ADJC_DIR = [(-1, 0), (0, 1), (1, 0), (0, -1)]
ALL_DIR = [(1, 1), (1, -1), (1, 0), (0, 1),
           (0, -1), (-1, 1), (-1, 0), (-1, -1)]


def calculateTStar(currentState, size: int, grid, states: dict):
    # remove dog actions if he near in a wall or something
    # we can consider actions by their results, these are all the possible actions
    resultStates = [((currentState[0][0] + i[0], currentState[0][1] + i[1]), (currentState[1][0], currentState[1][1]))
                    for i in ALL_DIR if onGrid(grid, currentState[0][0] + i[0], currentState[0][1] + i[1])]

    def expectedTofSheepMove(state):
        possibleActionsOfSheep = []
        deltaY = state[0][0] - state[1][0]
        deltaX = state[0][1] - state[1][1]
        if abs(deltaX) <= 2 or abs(deltaY) <= 2:
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

            # remove directions of sheep that are not possible
        return sum([1/len(possibleActionsOfSheep) * states[(state[0], (state[1][0] + i[0], state[1][1] + i[1]))] for i in possibleActionsOfSheep])

    return BETA * min(list(map(expectedTofSheepMove, resultStates))) + 1


start = time.time()

grid: list[list[bool]] = None
states: dict = None

grid, states = setupEnvironment(51)

f = open("storing_info", "a")
for i in states:
    f.write(str(i) + " " + str(states[i]) + "\n")
f.close()

end = time.time()

print(end - start)


numSheepPenned: int = 0
numSheepToPen = 100000000


for i in range(numSheepToPen):

    state = ((Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)),
             (Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)))
    while (not grid[state[0][0]][state[0][1]] and not grid[state[1][0]][state[1][1]]):
        state = ((Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)),
                 (Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)))

    while (True):
        if (state[0] == state[1]):
            break
        if state[1] != (int((len(grid) - 1)/2), int((len(grid) - 1)/2)):
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
        if abs(deltaX) <= 2 or abs(deltaY) <= 2:
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
