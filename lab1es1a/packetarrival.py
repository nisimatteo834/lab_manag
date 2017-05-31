import simpy
import random
import numpy
from decimal import Decimal
from matplotlib import pyplot


INTER_ARRIVAL = 25
SERVICE_TIME = 1
NUM_MACHINES = 1
SIM_TIME = 100000

class PacketArrival(object):

    def __init__(self, environ, arrival_time):

        self.arrival_time = arrival_time
        self.env = environ

    def arrival_process(self, buffer):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)
            yield self.env.timeout(inter_arrival)

            # a packet has arrived - request buffer to do its job
            self.env.process(buffer.process())

