#!/usr/bin/python3

import simpy
import random
import numpy
from matplotlib import pyplot

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 2.0
SERVICE_TIME = 3.0
NUM_MACHINES = 2

SIM_TIME = 10000

# **********************************************************************************************************************
# Car arrival
# **********************************************************************************************************************
class CarArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        self.inter_arrival = []
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

            self.inter_arrival.append(inter_arrival)

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

    def wash(self):
        print("Cars in the shop on arrival: ", self.qsize, self.env.now)

        self.qsize += 1

        # request a machine to wash the new coming car
        with self.machines.request() as request:
            yield request

            self.sonoarrivata = self.env.now

            # once the machine is free, wait until service is finished
            service_time = 2#random.expovariate(lambd=1.0/self.service_time)

            # yield an event to the simulator
            yield self.env.timeout(service_time)


            # release the wash machine
            self.qsize -= 1

            self.hofinito = self.env.now - self.sonoarrivata
            print (self.hofinito)

            # the "with" statement implicitly delete request here "releasing" the resource

# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    # ********************************
    # setup and perform the simulation
    # ********************************

    env = simpy.Environment()

    # car arrival


    car = CarArrival(env, INTER_ARRIVAL)

    # carwash
    carwash = Carwash(env, NUM_MACHINES, SERVICE_TIME)

    # start the arrival process
    env.process(car.arrival_process(carwash))

    # simulate until SIM_TIME
    env.run(until=SIM_TIME)

    fig, (series, pdf, cdf) = pyplot.subplots(3, 1)
    series.plot(car.inter_arrival)
    series.set_xlabel("Sample")
    series.set_ylabel("Inter-arrival")
    pdf.hist(car.inter_arrival, bins=100, normed=True)
    pdf.set_xlabel("Time")
    pdf.set_ylabel("Density")
    pdf.set_xbound(0, 15)
    cdf.hist(car.inter_arrival, bins=100, cumulative=True, normed=True)
    cdf.set_xlabel("Time")
    cdf.set_ylabel("P(Arrival time <= x)")
    cdf.set_ybound(0, 1)
    cdf.set_xbound(0, 15)
    pyplot.show()