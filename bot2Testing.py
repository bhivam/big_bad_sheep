from random import Random

# weights = (4.50111182, -2.4612226,  -0.38125132,  3.8872709, 1.85558595, 10.20977843,
#            5.08201357, -8.17399381, -2.89200154, -3.98879119,  3.91933393, -3.50907315,
#            -2.82206193,  0.97653898, -6.25791141)

# weights = (4.79608581,  0.07593788, -0.11643714,  0.47773051,  0.43812455,  0.02494378,
#            0.16466934, -0.22100841, -0.19239507,  0.06980649, -0.15437872, -0.15133064,
#            -0.10378463, -0.09366338, -0.21306139)

# weights = (4.85921953,  0.03240334, -0.09187123,  0.33425678,  0.30660856,  0.0372939,
#            0.12739401, -0.1376795,  -0.1171069,   0.06253214, -0.11858945, -0.1185348,
#            -0.08531716, -0.07784065, -0.15596228)

weights = (4.97823080e+00, -5.99445100e-02, -8.28917853e-02,  9.51229721e-02,
           8.44758916e-02,  6.63610185e-02,  8.31782954e-02, -2.20589710e-03,
           6.33861892e-03,  6.23903268e-02, -5.61152541e-02, -6.06593880e-02,
           -4.83270997e-02, -4.56888734e-02, -6.11160250e-02)

PEN = set([(1, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 1)])
ALL_DIR = [(1, 1), (1, -1), (1, 0), (0, 1),
           (0, -1), (-1, 1), (-1, 0), (-1, -1)]
PEN_LOCS = set()

f = open("machine_learning_test_data", "r")
rawStates = f.readlines()

rawStates = [i.strip().replace("(", "").replace(")", "").replace(
    ",", "").split(" ") for i in rawStates]

rawStates = [[int(i[0]), int(i[1]), int(i[2]), int(i[3]), float(i[4])]
             for i in rawStates]

# x1, x2, x3, x4, all squared values, all pairs of two multiplied together
# this is to set up a quadratic feature space
states = {(1, i[0], i[1], i[2], i[3],
           i[0] * i[0], i[1] * i[1], i[2] * i[2], i[3] * i[3],
           i[0] * i[1], i[0] * i[2], i[0] * i[3], i[1] * i[2],
           i[1] * i[3], i[2] * i[3],): float(i[4])
          for i in rawStates}


def dotProduct(x, y):
    # calculates dot product between two arrays of equal length
    assert(len(x) == len(y))
    sum = 0
    for i in range(len(x)):
        sum += x[i] * y[i]
    return sum


def onGrid(grid, x, y):
    return x >= 0 and x < len(grid) and y >= 0 and y < len(grid) and (x, y) not in PEN_LOCS


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


numSheepPenned: int = 0
numSheepToPen = 10000
grid = getGrid(15)


def toQuadraticState(normalState):
    # turns a normal state into the quadratic version so that the model can be applied
    return (1, normalState[0], normalState[1], normalState[2], normalState[3],
            normalState[0] * normalState[0], normalState[1] *
            normalState[1], normalState[2] *
            normalState[2], normalState[3] * normalState[3],
            normalState[0] * normalState[1], normalState[0] *
            normalState[2], normalState[0] *
            normalState[3], normalState[1] * normalState[2],
            normalState[1] * normalState[3], normalState[2] * normalState[3],)


for i in range(numSheepToPen):

    state = list(states.keys())[Random().randint(0, len(states) - 1)]
    while (grid[state[1]][state[2]] or grid[state[3]][state[4]]):
        state = list(states.keys())[Random().randint(0, len(states) - 1)]
    while (True):
        print(state)
        if (state[1] == state[3] and state[2] == state[4]):
            break
        if state[1] == int((len(grid) - 1)/2) and state[2] == int((len(grid) - 1)/2):
            numSheepPenned += 1
            break
        resultStates = [toQuadraticState((state[1] + i[0], state[2] + i[1], state[3], state[4]))
                        for i in ALL_DIR if onGrid(grid, state[1] + i[0], state[2] + i[1])]

        minState = resultStates[0]
        # only difference is that this algorithm will use the dot product of the weights and
        # state inputs to find the T value to minimize.
        for resultState in resultStates:
            if dotProduct(resultState, weights) < dotProduct(minState, weights):
                minState = resultState

        state = minState

        possibleActionsOfSheep = []
        deltaY = state[1] - state[3]
        deltaX = state[2] - state[4]
        if abs(deltaX) <= 2 and abs(deltaY) <= 2:
            if deltaY >= 0 and onGrid(grid, state[3] + 1, state[4] + 0):
                possibleActionsOfSheep.append((1, 0))
            if deltaY <= 0 and onGrid(grid, state[3] - 1, state[4] + 0):
                possibleActionsOfSheep.append((-1, 0))
            if deltaX >= 0 and onGrid(grid, state[3] + 0, state[4] + 1):
                possibleActionsOfSheep.append((0, 1))
            if deltaX <= 0 and onGrid(grid, state[3] + 0, state[4] - 1):
                possibleActionsOfSheep.append((0, -1))
        else:
            if onGrid(grid, state[3] + 1, state[4] + 0):
                possibleActionsOfSheep.append((1, 0))
            if onGrid(grid, state[3] - 1, state[4] + 0):
                possibleActionsOfSheep.append((-1, 0))
            if onGrid(grid, state[3] + 0, state[4] + 1):
                possibleActionsOfSheep.append((0, 1))
            if onGrid(grid, state[3] + 0, state[4] - 1):
                possibleActionsOfSheep.append((0, -1))

        if len(possibleActionsOfSheep) == 0:
            break
        sheepChoice = Random().randint(0, len(possibleActionsOfSheep) - 1)

        state = toQuadraticState((state[1], state[2], state[3] + possibleActionsOfSheep[sheepChoice]
                                 [0], state[4] + possibleActionsOfSheep[sheepChoice][1]))
    print(state)


print(numSheepPenned/numSheepToPen)
