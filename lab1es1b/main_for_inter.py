#!/usr/bin/python3

import simpy
import numpy
from matplotlib import pyplot
import random
from packet import Packet
from service import Service
from arrival import PacketArrival
import math
from scipy.stats import t


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 50
INTER_ARRIVAL = 15
SERVICE_TIME = 10
NUM_MACHINES = 1
MAX_BATCH = 10
SIM_TIME = 100000
MIN_BATCH = 1
BUFFER_SIZE = 5



total_enviroment = []


if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    env = simpy.Environment()
    car_arrival = PacketArrival(env, INTER_ARRIVAL)
    service = Service(env, NUM_MACHINES, SERVICE_TIME)
    env.process(car_arrival.arrival_process(service))
    env.run(until=SIM_TIME)

    meanResponseTimeWarmUp = numpy.mean(service.response_time)

    total_enviroment.append(service.response_time)

    countSimTime = 2
    NUM_EXPERIMENTS = 0
    confidence = (0,100)
    RememberConfidence = []
    meanResponseTime = []

    while True:

        # simulates until SIM_TIME
        env.run(until=SIM_TIME * countSimTime)

        countSimTime += 1
        NUM_EXPERIMENTS += 1

        # RESPONSE TIME
        responseTime = service.response_time
        total_enviroment.append(service.response_time)

        # appending Xi
        meanResponseTime.append(numpy.mean(responseTime))
        meanResponseExperiments = numpy.mean(meanResponseTime)

        if (NUM_EXPERIMENTS > 2):
            sigma = numpy.std(meanResponseTime)
            print "Standard deviation is: ", sigma
            confidence = t.interval(0.99, NUM_EXPERIMENTS - 1, meanResponseExperiments,
                                    math.sqrt(sigma / (NUM_EXPERIMENTS - 1)))
            print "Confidence interval is:", confidence
            RememberConfidence.append(confidence)

        # print "Start time: ", service.startTime
        # print "End time: ", service.endTime
        print "Response time of warm up is: ", meanResponseTimeWarmUp
        print "Response time is: ", meanResponseTime
        print "Mean response time of everything is: ", meanResponseExperiments
        print "Number of experiments: ", NUM_EXPERIMENTS - 1
        print "Confidence intervals: ", RememberConfidence

        stopCondition = (confidence[1] - confidence[0]) / meanResponseExperiments
        if (stopCondition < 0.05):
            break

print(total_enviroment)
pyplot.plot(total_enviroment)
pyplot.show()










