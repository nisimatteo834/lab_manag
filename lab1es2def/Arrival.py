


import simpy
import numpy
from decimal import Decimal
from matplotlib import pyplot
import random
import Queue


class Arrival(object):

    # constructor
    def __init__(self, environ, arrival_time, min_batch, max_batch):

        # the inter-arrival time
        self.arrival_time = arrival_time
        self.min_batch = min_batch
        self.max_batch = max_batch
        # the environment
        self.env = environ
        self.totalPackets = 0
        self.packetstosend = []

    # execute the process
    def arrival_process(self, cacheplusweb):
        while True:                             # never exit the loop

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            number_packets = numpy.random.uniform(self.min_batch, self.max_batch, 1).__int__()

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            print ('At', self.env.now, 'enter', number_packets, 'packets')
            # all the packets of the batches are dealt at the same time
            for x in range(0,number_packets):
                # a car has arrived - request cacheplusweb to do its job
                self.totalPackets += 1
                print (self.totalPackets, ' enters at ', self.env.now)
                self.env.process(cacheplusweb.frontEnd(self.totalPackets))