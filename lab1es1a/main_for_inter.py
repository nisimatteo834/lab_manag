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
    car_arrival = PacketArrival(env, INTER_ARRIVAL)
    service = Buffer(env, NUM_MACHINES, SERVICE_TIME)
    env.process(car_arrival.arrival_process(service))
    initial_esperiment = 1
    env.run(until=SIM_TIME*initial_esperiment)
    total_rt.append(numpy.mean(service.response_time))
    meanResponseTimeWarmUp = numpy.mean(service.response_time)

    countSimTime = 2
    NUM_EXPERIMENTS = 0
    confidence = (0,500)
    RememberConfidence = []
    meanResponseTime = []

    flag = False

    while True:

        # simulates until SIM_TIME
        env.run(until=SIM_TIME * countSimTime)

        countSimTime += 1
        NUM_EXPERIMENTS += 1

        # RESPONSE TIME
        responseTime = service.response_time
        total_rt.append(numpy.mean(responseTime))

        # appending Xi
        meanResponseTime.append(numpy.mean(responseTime))
        meanResponseExperiments = numpy.mean(meanResponseTime)

        if (NUM_EXPERIMENTS > 2):
            sigma = numpy.std(meanResponseTime)
            print ("Standard deviation is: ", sigma)
            confidence = t.interval(0.99, NUM_EXPERIMENTS - 1, meanResponseExperiments,
                                    math.sqrt(sigma / (NUM_EXPERIMENTS - 1)))
            print ("Confidence interval is:", confidence)
            RememberConfidence.append(confidence)

        # print "Start time: ", service.startTime
        # print "End time: ", service.endTime
        print("Response time of warm up is: ", meanResponseTimeWarmUp)
        print ("Response time is: ", meanResponseTime)
        print ("Mean response time of everything is: ", meanResponseExperiments)
        print ("Number of experiments: ", NUM_EXPERIMENTS - 1)
        print ("Confidence intervals: ", RememberConfidence)



        stopCondition = (confidence[1] - confidence[0]) / meanResponseExperiments
        if (stopCondition < 0.01):
            if flag is False:
                print (confidence[1],confidence[0],stopCondition,meanResponseExperiments)
                meanResponseTime.append(meanResponseExperiments)
                flag = True
            else:
                pyplot.figure()
                pyplot.plot(RememberConfidence,c='green')
                pyplot.plot(meanResponseTime[initial_esperiment+1:-1])

                pyplot.figure()
                pyplot.plot(total_rt[initial_esperiment+1:-1])
                pyplot.plot(RememberConfidence,c='green')
                pyplot.show()

            #break












