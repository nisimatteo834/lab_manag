#!/usr/bin/python3

import simpy
import random
import Queue


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************

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

        self.q_memory = [0]
        self.qsize = 0

        self.response_time = []

        self.numberPacketDropped = 0


    def wash(self,packetreceived):
        self.qsize += 1

        if self.qsize > BUFFER_SIZE:
            print ('Packet',packetreceived,'dropped')
            self.qsize -= 1
            self.numberPacketDropped += 1
            self.q_memory.append(self.qsize)

        else:
            enter = self.env.now
            self.q_memory.append(self.qsize)
            with self.machines.request() as request:
                print (packetreceived,'is asking for resource',self.env.now)
                yield request

                print(packetreceived,'get the resource',self.env.now)
                yield self.env.timeout(random.expovariate(lambd=1.0/self.service_time))
                print (packetreceived,'ends at',self.env.now)
                self.qsize -= 1
                self.q_memory.append(self.qsize)

            self.response_time.append(self.env.now-enter)












        #
        #
        # print("Cars in the shop in queue: ", self.queue.qsize())
        # flag = True
        # while (self.queue.qsize() != 0 or flag is True):
        #     enter = self.env.now
        # # request a machine to wash the new coming car
        #     with self.machines.request() as request:
        #         yield request
        #
        #     # once the machine is free, wait until service is finished
        #         service_time = random.expovariate(lambd=1.0/self.service_time)
        #         packetserved = self.queue.get()
        #         print ('Packet ', packetserved.getId(), 'start washing at', self.env.now)
        #     # yield an event to the simulator
        #     #todo
        #
        #     print ('Packet ', packetserved.getId(), 'end washed at', self.env.now)
        #     # release the wash machine
        #     self.response_time.append(self.env.now-enter)


