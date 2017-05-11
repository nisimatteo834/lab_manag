#!/usr/bin/python3

import simpy
import random
import numpy

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 15
SERVICE_TIME = 10
NUM_MACHINES = 1

SIM_TIME = 1000

# **********************************************************************************************************************
# Car arrival
# **********************************************************************************************************************
class CarArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time
        self.count = 0
        # the environment
        self.env = environ
        self.servicetime = []
        self.enter = []
        self.exit = []
    # execute the process
    def arrival_process(self, carwash):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)
            self.count +=1
            # yield an event to the simulator
            self.enter.append(self.env.now)
            yield self.env.timeout(inter_arrival)
            #print (self.count,'ENTER',enter,'AFTER IA',self.env.now)

            # a car has arrived - request carwash to do its job
            yield self.env.process(carwash.wash())
            # print (self.count,'ENTER',enter,'END',self.env.now)

            self.exit.append(self.env.now)



# **********************************************************************************************************************
# Car wash - it gets an waiting car (FCFS) and performs the service
# **********************************************************************************************************************
class Carwash(object):

    # constructor
    def __init__(self, environ, num_machines, service_time):

        # the service time
        self.service_time = service_time

        # wash machines
        # the environment
        self.env = environ
        self.machines = simpy.Resource(environ, num_machines)

        # number of cars in the shop
        self.qsize = 0

    def wash(self):
        print("Cars in the shop on arrival: ", self.qsize)

        self.qsize += 1

        # request a machine to wash the new coming car
        with self.machines.request() as request:
            yield request

            # once the machine is free, wait until service is finished
            service_time = random.expovariate(lambd=1.0/self.service_time)
            print (service_time)

            # yield an event to the simulator
            yield self.env.timeout(service_time)

            # release the wash machine
            self.qsize -= 1

        # the "with" statement implicitly delete request here "releasing" the resource

# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    # ********************************
    # setup and perform the simulation
    # ********************************

    avg_s_time = []
    for miu_t in range(SERVICE_TIME,INTER_ARRIVAL,1):
        env = simpy.Environment()
        car_arrival = CarArrival(env, INTER_ARRIVAL)
        carwash = Carwash(env, NUM_MACHINES, miu_t)
        env.process(car_arrival.arrival_process(carwash))
        env.run(until=SIM_TIME)

        sub =[]

        for x in range(0,len(car_arrival.exit)):
            sub.append(car_arrival.exit[x]-car_arrival.enter[x])
        avg_s_time.append(numpy.mean(sub))

    print (avg_s_time)



