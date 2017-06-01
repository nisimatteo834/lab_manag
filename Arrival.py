import simpy
import random
import numpy

class Arrival(object):

    def __init__(self, environment, arrivalRate, minBatch, maxBatch):

        # store all  intervals between arrivals that are generated
        self.interArrival = []

        # arrival rate
        self.arrivalRate = arrivalRate

        # environment
        self.env = environment

        # parameters for the uniform distribution used in batch
        self.minBatch = minBatch
        self.maxBatch = maxBatch

        # store the number of arrivals at once
        self.batch = []

        self.totalPackets = 0


    def arrival(self, service):

        while True:

            # sample the time to the next arrival
            self.interArrival.append(random.expovariate(lambd=1.0/self.arrivalRate))

            # sample the number of packets that will arrive at the same time
            self.batch.append(random.uniform(self.minBatch, self.maxBatch))

            # wait for time defined by interArrival
            yield self.env.timeout(self.interArrival[-1])

            # fill buffer occupancy
            # yield self.env.timeout(10)
            # self.env.process(service.bufferOccupancy())
            # print self.env.now


            # print ('At instant ', self.env.now, "the number of packets arriving is ", int(self.batch[-1]))

            # call the process many times (= number of packets arriving at the same time)
            for i in range(0, int(self.batch[-1])):
                self.totalPackets += 1
                if i != int(self.batch[-1]):
                    self.env.process(service.job(False))
                else:
                    self.env.process(service.job(True))
