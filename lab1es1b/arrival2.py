#!/usr/bin/python3

import numpy
import random
from packet import Packet
from service2 import Service



# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************

MIN_BATCH = 1
MAX_BATCH = 10

# **********************************************************************************************************************
# Car arrival
# **********************************************************************************************************************
class PacketArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time
        # the environment
        self.env = environ
        self.count = 0
        self.packetstosend = []

    # execute the process
    def arrival_process(self, service):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            number_packets = numpy.random.uniform(MIN_BATCH,MAX_BATCH,1).__int__()

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            #print ('At', self.env.now, 'enter', number_packets, 'packets')

            for x in range(0,number_packets):
                self.count +=1
                self.env.process(service.wash(self.count))
