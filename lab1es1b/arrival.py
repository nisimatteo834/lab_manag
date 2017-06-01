#!/usr/bin/python3

import numpy
import random
from packet import Packet



# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 50
INTER_ARRIVAL = 15
SERVICE_TIME = 1#todo put it to 1 in order to have a good plot
NUM_MACHINES = 1
MAX_BATCH = 10
SIM_TIME = 100000
MIN_BATCH = 1
BUFFER_SIZE = 5

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
    def arrival_process(self, carwash):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            number_packets = numpy.random.uniform(MIN_BATCH,MAX_BATCH,1).__int__()

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            #print ('At', self.env.now, 'enter', number_packets, 'packets')

            for x in range(0,number_packets):
                # a car has arrived - request carwash to do its job
                self.count += 1
                p = Packet(self.count)
                self.packetstosend.append(p)
                #print (p.getId(),' enters at ',self.env.now)
            self.env.process(carwash.wash(self.packetstosend))