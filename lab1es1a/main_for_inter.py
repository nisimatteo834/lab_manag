#!/usr/bin/python3

from __future__ import print_function
import simpy
import numpy
from matplotlib import pyplot
import random
from process import Buffer
from packetarrival import PacketArrival
import math
from scipy.stats import t


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 50
INTER_ARRIVAL = 15
SERVICE_TIME = 14
NUM_MACHINES = 1
SIM_TIME = 1000000


if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    total_rt = []

    env = simpy.Environment()
    packet_arrival = PacketArrival(env, INTER_ARRIVAL)
    service = Buffer(env, NUM_MACHINES, SERVICE_TIME)
    env.process(packet_arrival.arrival_process(service))
    initial_esperiment = 1
    env.run(until=SIM_TIME*initial_esperiment)
    total_rt.append(numpy.mean(service.response_time))
    meanResponseTimeWarmUp = numpy.mean(service.response_time)

    counter = 2
    exp = 0
    confidence = (0,500)
    HistoryConf = []
    meanResponseTime = []

    flag = False

    while True:

        # simulates until SIM_TIME
        env.run(until=SIM_TIME * counter)

        responseTime = service.response_time
        counter += 1
        exp += 1


        meanResponseTime.append(numpy.mean(responseTime))
        meanExp = numpy.mean(meanResponseTime)

        if (exp > 2):
            sigma = numpy.std(meanResponseTime)
            confidence = t.interval(0.99, exp - 1, meanExp,
                                    math.sqrt(sigma / (exp - 1)))
            HistoryConf.append(confidence)


        stopCondition = (confidence[1] - confidence[0]) / meanExp
        if (stopCondition < 0.01):
            print (confidence[1],confidence[0],stopCondition,meanExp)
            meanResponseTime.append(meanExp)

            #a way to have better plot
            if exp > 30:
                pyplot.figure()
                pyplot.plot(HistoryConf,c='green')
                pyplot.plot(meanResponseTime[initial_esperiment+1:-1])
                break














