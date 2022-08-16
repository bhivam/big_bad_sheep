from random import Random
import numpy as np

# learning rate
ALPHA = 0.00005

# reads in all of the states to be trained on
f = open("storing_info1", "r")
rawStates = f.readlines()

rawStates = [i.strip().replace("(", "").replace(")", "").replace(
    ",", "").split(" ") for i in rawStates]
# process the states to make the data easy to work with

# only get the non outlier states so that the model doesn't try to fit infinity
rawStates = [[int(i[0])/25, int(i[1])/25, int(i[2])/25, int(i[3])/25, float(i[4])]
             for i in rawStates if float(i[4]) < 9999999 and float(i[4]) > 1]

# x1, x2, x3, x4, all squared values, all pairs of two multiplied together
# this is to set up a quadratic input space
# actual T* tagged on at the end of the vector.
states = np.array([np.array([1, i[0], i[1], i[2], i[3],
                             i[0] * i[0], i[1] * i[1], i[2] * i[2], i[3] * i[3],
                             i[0] * i[1], i[0] * i[2], i[0] * i[3], i[1] * i[2],
                             i[1] * i[3], i[2] * i[3], float(i[4])]) for i in rawStates])

# states = {(1, i[0], i[1], i[2], i[3]): float(i[4])
#           for i in rawStates}

# this initialized the weights
weights = np.array([Random().random() * 20 -
                    10 for i in range(15)])


def calculateLoss():
    # takes 10000 random states and find the mean squared loss based on the weights
    meanSquaredLoss = 0
    for i in range(10000):
        state = states[Random().randint(0, len(states) - 1)]

        # the dot product of the weights and the inputs minus the actual T* squared is added to the meanSquaredLoss
        meanSquaredLoss += (np.dot(weights, state[0:-1]) -
                            state[-1]) ** 2
    meanSquaredLoss /= 10000  # divide by the number of data points
    return meanSquaredLoss


while True:
    for i in range(100000):
        # print weights and loss every 100000 updates of the weights
        # get a random weight to SGD
        randomState = states[Random().randint(0, len(states) - 1)]
        # estimate the value to be plugged into the derivative
        estimatedValue = np.dot(weights, randomState[0:-1])
        weights = np.subtract(weights, np.multiply(
            ALPHA * (estimatedValue - randomState[-1]), randomState[0:-1]))
        # calculate the updated value by subtracting the estimate from the real value, then multiplying the
        # alpha and randomly chosen state, then subtracting it from the current weights.
    print(weights)
    print(calculateLoss())
