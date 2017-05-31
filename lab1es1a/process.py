import simpy
import random
import numpy
from decimal import Decimal
from matplotlib import pyplot

class Buffer(object):

    # constructor
    def __init__(self, environ, num_machines, service_time):

        # the service time
        self.service_time = service_time

        # process machines
        self.machines = simpy.Resource(environ, num_machines)

        # the environment
        self.env = environ

        # number of cars in the shop
        self.qsize = 0

        self.q_memory = []

        self.response_time = []

    def process(self):
        print("Cars in the shop on arrival: ", self.qsize)

        self.q_memory.append(self.qsize)
        self.qsize += 1



        enter = self.env.now

        # request a machine to process the new coming car
        with self.machines.request() as request:
            yield request

            # once the machine is free, wait until service is finished
            service_time = random.expovariate(lambd=1.0/self.service_time)

            # yield an event to the simulator
            yield self.env.timeout(service_time)

            # release the process machine
            self.qsize -= 1

            self.response_time.append(self.env.now-enter)
