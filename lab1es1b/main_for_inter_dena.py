# Calculating the confidence interval

import simpy
import random
from arrival import CarArrival as Arrival
from service import Carwash as Service
import numpy
from matplotlib import pyplot
import math
from scipy.stats import t

###########################################
# Main
###########################################

if __name__ == "__main__":

    ARRIVAL_TIME = 5
    SERVICE_TIME = 10.
    NUM_SERVERS = 1

    SIM_TIME = 1000

    MIN_BATCH = 1
    MAX_BATCH = 4
    E_batch = (MIN_BATCH + MAX_BATCH) / 2
    BUFFER_SIZE = 10
    B = BUFFER_SIZE + 1

    meanResponseTime = []

    # creates Environment
    env = simpy.Environment()
    # initializes arrivals
    packet = Arrival(env, ARRIVAL_TIME, MIN_BATCH, MAX_BATCH)

    # initializes service
    service = Service(env, SERVICE_TIME, NUM_SERVERS, BUFFER_SIZE)

    # starts the arrival process
    env.process(packet.arrival(service))

    env.run(until=SIM_TIME)

    responseTimeWarmUp = []
    for m in range(len(service.endTime)):
        responseTimeWarmUp.append(service.endTime.pop(0) - service.startTime.pop(0))

    meanResponseTimeWarmUp = numpy.mean(responseTimeWarmUp)

    countSimTime = 2
    NUM_EXPERIMENTS = 0
    confidence = (0, 500)
    RememberConfidence = []

    # while (confidence):
    while True:

        # simulates until SIM_TIME
        env.run(until=SIM_TIME * countSimTime)

        countSimTime += 1
        NUM_EXPERIMENTS += 1

        # RESPONSE TIME
        responseTime = []
        for m in range(len(service.endTime)):
            responseTime.append(service.endTime.pop(0) - service.startTime.pop(0))

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

            print "Start time: ", service.startTime
            print "End time: ", service.endTime
            print "Response time of warm up is: ", meanResponseTimeWarmUp
            print "Response time is: ", meanResponseTime
        print "Mean response time of everything is: ", meanResponseExperiments
        print "Number of experiments: ", NUM_EXPERIMENTS - 1
        print "Confidence intervals: ", RememberConfidence

        stopCondition = (confidence[1] - confidence[0]) / meanResponseExperiments
        if (stopCondition < 0.05):
            break



