#!/usr/bin/python3

import simpy
import random
import Queue


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


class Service(object):

    # constructor
    def __init__(self, environ, num_machines, service_time):

        # the service time
        self.service_time = service_time

        # wash machines
        self.machines = simpy.Resource(environ, num_machines)

        # the environment
        self.env = environ

        # number of cars in the shop

        self.q_memory = []

        self.queue = Queue.Queue()

        self.response_time = []

        self.numberPacketDropped = 0


    def wash(self,packetreceived):

        for x in range(0,len(packetreceived)):
            if  (self.queue.qsize()< BUFFER_SIZE):
                self.queue.put(packetreceived[0])
                #print ('Packet ',packetreceived[0].getId(),'in queue at ',self.env.now)
                packetreceived.remove(packetreceived[0])
            else:
                #print ('Packet ',packetreceived[0].getId(),'has been dropped ',self.env.now)
                packetreceived.remove(packetreceived[0])
                self.numberPacketDropped += 1

        self.q_memory.append(self.queue.qsize())
        #print("Cars in the shop in queue: ", self.queue.qsize())

        while (not self.queue.empty()):
            enter = self.env.now
        # request a machine to wash the new coming car
            with self.machines.request() as request:
                yield request

            # once the machine is free, wait until service is finished
                service_time = random.expovariate(lambd=1.0/self.service_time)
                packetserved = self.queue.get()
                #print ('Packet ', packetserved.getId(), 'start washing at', self.env.now)
            # yield an event to the simulator
            yield self.env.timeout(service_time)

            #print ('Packet ', packetserved.getId(), 'end washed at', self.env.now)
            # release the wash machine
            self.response_time.append(self.env.now-enter)
