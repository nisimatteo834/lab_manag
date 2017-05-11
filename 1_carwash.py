#!/usr/bin/python3

import simpy
import random
import numpy
from decimal import Decimal


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 25
SERVICE_TIME = 1
NUM_MACHINES = 1

SIM_TIME = 100000

# **********************************************************************************************************************
# Car arrival
# **********************************************************************************************************************
class CarArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time

        # the environment
        self.env = environ

    # execute the process
    def arrival_process(self, carwash):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)


            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)

            # a car has arrived - request carwash to do its job
            self.env.process(carwash.wash())


# **********************************************************************************************************************
# Car wash - it gets an waiting car (FCFS) and performs the service
# **********************************************************************************************************************
class Carwash(object):

    # constructor
    def __init__(self, environ, num_machines, service_time):

        # the service time
        self.service_time = service_time

        # wash machines
        self.machines = simpy.Resource(env, num_machines)

        # the environment
        self.env = environ

        # number of cars in the shop
        self.qsize = 0

        self.response_time = []

    def wash(self):
        print("Cars in the shop on arrival: ", self.qsize)

        self.qsize += 1

        enter = self.env.now

        # request a machine to wash the new coming car
        with self.machines.request() as request:
            yield request

            # once the machine is free, wait until service is finished
            service_time = random.expovariate(lambd=1.0/self.service_time)

            # yield an event to the simulator
            yield self.env.timeout(service_time)

            # release the wash machine
            self.qsize -= 1

            self.response_time.append(self.env.now-enter)

        # the "with" statement implicitly delete request here "releasing" the resource

# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    # ********************************
    # setup and perform the simulation
    # ********************************

    averag = []
    theoretical  = []

    for x in range(SERVICE_TIME,INTER_ARRIVAL,1):
        env = simpy.Environment()

        # car arrival
        car_arrival = CarArrival(env, INTER_ARRIVAL)

        # carwash
        carwash = Carwash(env, NUM_MACHINES, x)

        # start the arrival process
        env.process(car_arrival.arrival_process(carwash))

        # simulate until SIM_TIME
        env.run(until=SIM_TIME)


        averag.append(numpy.mean(carwash.response_time))
        ro = float(x)/INTER_ARRIVAL
        print (ro)
        print ('ro',ro,'E[T]',float(1)/(float(1)/x-float(1)/INTER_ARRIVAL))
        theoretical.append(float(1)/(float(1)/x-float(1)/INTER_ARRIVAL))






