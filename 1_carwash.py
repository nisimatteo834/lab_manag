#!/usr/bin/python3

import simpy
import random
import numpy
from matplotlib import pyplot
import math

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 5.0
SERVICE_TIME = 3.0
NUM_MACHINES = 1

mu = 1/SERVICE_TIME
yambda = 1/INTER_ARRIVAL

SIM_TIME = 10000

# **********************************************************************************************************************
# Car arrival
# **********************************************************************************************************************
class CarArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        self.inter_arrival = []
        self.permanence_time = []
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
        self.service_time = random.expovariate(lambd=1.0/service_time)


        # wash machines
        self.machines = simpy.Resource(env, num_machines)

        # the environment
        self.env = environ

        # number of cars in the shop
        self.buffer_occupancy = []
        self.permanence_time = []
        self.qsize = 0

    def wash(self):
        print("Cars in the shop on arrival: ", self.qsize, self.env.now)

        self.sonoarrivata = self.env.now
        self.qsize += 1
        self.buffer_occupancy.append(self.qsize)

        # request a machine to wash the new coming car
        with self.machines.request() as request:
            yield request



            # once the machine is free, wait until service is finished
            service_time = random.expovariate(lambd=1.0/self.service_time)

            # yield an event to the simulator
            yield self.env.timeout(service_time)


            # release the wash machin
            self.qsize -= 1

            self.permanence_time.append(self.env.now - self.sonoarrivata)

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


    fig, (series, pdf, cdf, kdf) = pyplot.subplots(4, 1)
    series.hist(car.inter_arrival,bins = 100, normed=True)
    series.set_xlabel("Sample")
    series.set_ylabel("Inter-arrival")
    y = carwash.buffer_occupancy
    x = numpy.linspace(0,y.__len__(),y.__len__())
    pdf.plot(y)
    pdf.set_xlabel("Time")
    pdf.set_ylabel("BO")
    pdf.set_xbound(0,y.__len__())
    cdf.plot(carwash.permanence_time)
    cdf.set_xlabel("Time")
    cdf.set_ylabel("PT")


    kdf.hist(car.inter_arrival, bins=100, cumulative=True, normed=True)
    #kdf.set_xbound(0,14)
    #kdf.set_ybound(0,0.5)
    kdf.set_ylabel("P(A_t <= x)")


    print(carwash.permanence_time)
    print(car.inter_arrival)

    print(numpy.mean(carwash.permanence_time))

    ro = 1/(INTER_ARRIVAL/SERVICE_TIME)
    print (1/(mu-yambda)-(ro/(mu-yambda)))
    print(ro)
    pyplot.show()