from random import Random
import time


# to track the blocked cells
PEN = set([(1, 0), (1, -1), (1, 1), (0, -1), (0, 1), (-1, -1), (-1, 1)])
# to discount error in the infinite horizon value iteration
BETA = 0.99
# will contain all the pen locations
PEN_LOCS = set()


def setupEnvironment(size: int):
    # making sure the size is an odd number greater than five.
    center: int = int(size/2)
    if size < 5:
        size = 5
    if size % 2 == 0:
        size += 1
    # wherever the pen exits, add the pen location to the set of pen location
    # and indicate the pen location on the grid
    grid = [[False for i in range(size)]
            for j in range(size)]
    for i in PEN:
        grid[i[0] + center][i[1] + center] = True
        PEN_LOCS.add((i[0] + center, i[1] + center))

    # create a dictionary (hash map) to create a mapping from state to T*
    states: dict = {}
    # dog is first tuple, sheep is second tuple
    for i in range(size):
        for j in range(size):
            for k in range(size):
                for l in range(size):
                    # the dog's x and y, and the sheep's x and y lead to size^4 possible combinations
                    if (i, j) not in PEN_LOCS and (k, l) not in PEN_LOCS:
                        # the initial starting values are simply the sheep's manhattan distance from the pen
                        initialTStart: int = abs(k - center) + abs(l - center)
                        states[((i, j), (k, l))] = initialTStart
                        # the states is a tuple of two tuples, the first is the dogs position and the second is
                        # the sheep's position

    calculateTStars(states, size, grid)

    return grid, states


def calculateTStars(states: dict, size: int, grid):
    numStates = len(states)
    # track loss between rounds to terminate when the loss between rounds is low
    lossBetweenRounds = 0
    while True:
        for i in states:
            newState = 0
            if i[1] == (int(size/2), int(size/2)):
                # if the sheep reaches the center the T should be zero
                newState = 0
            elif i[1] == i[0]:
                # if the sheep and dog are in the same position the T should be infinite
                # I am using this arbitrarily high number to represent infinity
                newState = 999999999999999999
            else:
                # if neither of these special cases, get the T*
                newState = calculateTStar(i, size, grid, states)
            lossBetweenRounds += newState - states[i]
            # update the loss between rounds by subtracting the T* of this state by the new one
            states[i] = newState
        if (abs(lossBetweenRounds/numStates) < 0.001):
            # absolute value since negative loss is treated the same and divide by the number of states to have
            # a more manageable number.
            # this if statement at the end of the while loop makes an do while loop effectively
            break
        lossBetweenRounds = 0


def onGrid(grid, x, y):
    # helper function to see if a x y coordinate is valid
    return x >= 0 and x < len(grid) and y >= 0 and y < len(grid) and (x, y) not in PEN_LOCS


# to make life easier when iterating through possible actions
ADJC_DIR = [(-1, 0), (0, 1), (1, 0), (0, -1)]
ALL_DIR = [(1, 1), (1, -1), (1, 0), (0, 1),
           (0, -1), (-1, 1), (-1, 0), (-1, -1)]


def calculateTStar(currentState, size: int, grid, states: dict):
    # This gets all the possible dog actions as long as they are valid coordinates
    resultStates = [((currentState[0][0] + i[0], currentState[0][1] + i[1]), (currentState[1][0], currentState[1][1]))
                    for i in ALL_DIR if onGrid(grid, currentState[0][0] + i[0], currentState[0][1] + i[1])]

    def expectedTofSheepMove(state):
        possibleActionsOfSheep = []
        deltaY = state[0][0] - state[1][0]
        deltaX = state[0][1] - state[1][1]
        # this is going to add different actions to sheep's possible actions if the dog is within a 2 block
        # radius and then depending on if the resulting position is on the grid and the direction of the dog
        # from the sheep. The delta x and y explain both direction and radius while the on grid function will
        # tell if the function is valid or not.
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

        # this is making a list of the each possible action multiplied by its probability of occurring, summed
        # this takes care of the sum in value iteration.
        return sum([1/len(possibleActionsOfSheep) * states[(state[0], (state[1][0] + i[0], state[1][1] + i[1]))] for i in possibleActionsOfSheep])

    # this maps each dog state to an associated expected T*, finds the min, multiplies it by beta and adds one to it
    # to account for taking an action.
    return BETA * min(list(map(expectedTofSheepMove, resultStates))) + 1


start = time.time()

grid: list[list[bool]] = None
states: dict = None

grid, states = setupEnvironment(25)

f = open("storing_info", "a")
for i in states:
    f.write(str(i) + " " + str(states[i]) + "\n")
f.close()

end = time.time()

# tracking time to get good prediction of how long running the algorithm should take
print(end - start)


numSheepPenned: int = 0
numSheepToPen = 1000  # number of iterations of the simulation


for i in range(numSheepToPen):
    # to simulate, get a valid random state
    state = ((Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)),
             (Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)))
    while (grid[state[0][0]][state[0][1]] or grid[state[1][0]][state[1][1]]):
        state = ((Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)),
                 (Random().randint(0, len(grid) - 1), Random().randint(0, len(grid) - 1)))

    while (True):
        if (state[0] == state[1]):  # if the dog and the sheep are in the same state terminate
            break
        if state[1] == (int((len(grid) - 1)/2), int((len(grid) - 1)/2)):
            # increment the number of sheep penned if the sheep was penned then terminate.
            numSheepPenned += 1
            break

        # getting the possible dog actions
        resultStates = [((state[0][0] + i[0], state[0][1] + i[1]), (state[1][0], state[1][1]))
                        for i in ALL_DIR if onGrid(grid, state[0][0] + i[0], state[0][1] + i[1])]

        minState = resultStates[0]

        for resultState in resultStates:
            if states[resultState] < states[minState]:
                minState = resultState

        state = minState
        # calculating the action which leads to a state that has the smallest T*

        # calculating the sheep's movement same as above.
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
            # if the sheep can't do anything then the sheep passes its turn, otherwise it will move in a random
            # possible direction
            pass
        else:
            sheepChoice = Random().randint(0, len(possibleActionsOfSheep) - 1)

            state = (state[0], (state[1][0] + possibleActionsOfSheep[sheepChoice]
                                [0], state[1][1] + possibleActionsOfSheep[sheepChoice][1]))

# print the success rate
print(numSheepPenned/numSheepToPen)
