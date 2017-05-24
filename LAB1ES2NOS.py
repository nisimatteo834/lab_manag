#!/usr/bin/python3

import simpy
import numpy
from decimal import Decimal
from matplotlib import pyplot
import random
import Queue


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 50
INTER_ARRIVAL = 15
SERVICE_TIME = 10#todo put it to 1 in order to have a good plot
NUM_MACHINES = 1
MAX_BATCH = 10
SIM_TIME = 1000
MIN_BATCH = 1
BUFFER_SIZE = 15

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
        self.count = 0
        self.packetstosend = []

    # execute the process
    def arrival_process(self, cacheplusweb):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            number_packets = numpy.random.uniform(MIN_BATCH,MAX_BATCH,1).__int__()

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            print ('At', self.env.now, 'enter', number_packets, 'packets')

            for x in range(0,number_packets):
                # a car has arrived - request cacheplusweb to do its job
                self.count += 1
                p = Packet(self.count)
                self.packetstosend.append(p)
                print (p.getId(),' enters at ',self.env.now)

            self.env.process(cacheplusweb.frontEnd(self.packetstosend))



class Packet():
    def __init__(self,id):
        self.id = id

    def getId(self):
        return self.id
# **********************************************************************************************************************
# Car wash - it gets an waiting car (FCFS) and performs the service
# **********************************************************************************************************************
class cacheplusweb(object):

    # constructor
    def __init__(self, env,bs1,nm1,st1,bs2,nm2,st2,tsh):

        self.tsh = tsh
        # the service time
        self.bs1 = bs1
        self.st1 = st1
        self.nm1 = nm1

        self.bs2 = bs2
        self.nm2 = nm2
        self.st2 = st2


        # wash machines
        self.machines1 = simpy.Resource(env, nm1)
        self.machines2 = simpy.Resource(env,nm2)

        # the environment
        self.env = env

        # number of cars in the shop

        self.q_memory = []

        self.queue1 = Queue.Queue()
        self.queue2 = Queue.Queue()

        self.response_time1 = []
        self.response_time2 = []
        self.total_response_time = []

        self.bo1 = []
        self.bo2 = []

        self.numberPacketDropped = 0


    def frontEnd(self,packetreceived):

        for x in range(0,len(packetreceived)):
            if  (self.queue1.qsize()< self.bs1):
                self.queue1.put(packetreceived[0])
                print ('Packet ',packetreceived[0].getId(),'in Q1 at ',self.env.now)
                packetreceived.remove(packetreceived[0])
            else:
                print ('Packet ',packetreceived[0].getId(),'has been dropped by Q1 ',self.env.now)
                packetreceived.remove(packetreceived[0])
                self.numberPacketDropped += 1

        self.bo1.append(self.queue1.qsize())
        print("Cars in the shop in queue1: ", self.queue1.qsize())

        while (not self.queue1.empty()):
            enter = self.env.now
        # request a machine to wash the new coming car
            with self.machines1.request() as request:
                yield request

            # once the machine is free, wait until service is finished
                service_time = random.expovariate(lambd=1.0/self.st1)
                packetserved = self.queue1.get()
                print ('Packet ', packetserved.getId(), 'served by Q1 at', self.env.now)
            # yield an event to the simulator
            yield self.env.timeout(service_time)

            print ('Packet ', packetserved.getId(), 'exits from FrontEnd at ', self.env.now)
            # release the wash machine
            self.response_time1.append(self.env.now-enter)

            p = numpy.random.uniform(0,1)

            if p > tsh:
                yield (self.env.process(self.backEnd(packetserved)))

            else:
                self.response_time2.append(0)

            self.total_response_time.append(self.env.now-enter)
    def backEnd(self,packetreceived):
        if  (self.queue2.qsize()< self.bs2):
            self.queue2.put(packetreceived)
            print ('Packet ',packetreceived.getId(),'in Q2 at ',self.env.now)

        else:
            print ('Packet ',packetreceived[0].getId(),'has been dropped by Q2 ',self.env.now)
            self.numberPacketDropped += 1

        self.bo2.append(self.queue1.qsize())

        print("Packets in buffer2: ", self.queue2.qsize())

        while (not self.queue2.empty()):
            enter = self.env.now
        # request a machine to wash the new coming car
            with self.machines2.request() as request:
                print (packetreceived.getId(),'is asking for resource',request)
                yield request

                print (packetreceived.getId(),'is using the resource', request)


            # once the machine is free, wait until service is finished
                service_time = random.expovariate(lambd=1.0/self.st2)
                packetserved = self.queue2.get()
                print ('Packet ', packetserved.getId(), 'served in Q2 at', self.env.now)
            # yield an event to the simulator
            yield self.env.timeout(service_time)

            print ('Packet ', packetserved.getId(), 'end in Q2 at', self.env.now)
            # release the wash machine
            self.response_time2.append(self.env.now-enter)

# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    # ********************************
    # setup and perform the simulation
    # ********************************

    theoretical_buffer_occupancy = []
    average_buffer_occupancy = []
    average_response_time = []
    theoretical_response_time = []
    s_t_vector = []
    packetDroppedForSimulation = []
    dropOccurrence = []
    totalPacket = []
    testrun = []

    #todo scegliere come far variare il buffer size o il max batch per valutare

    #for x in range(SERVICE_TIME,INTER_ARRIVAL,1):
    env = simpy.Environment()

    # car arrival
    car_arrival = CarArrival(env, INTER_ARRIVAL)

    # cacheplusweb
    bs1 = BUFFER_SIZE
    bs2 = BUFFER_SIZE
    nm1 = NUM_MACHINES
    nm2 = NUM_MACHINES
    st1 = SERVICE_TIME/2
    st2 = SERVICE_TIME
    tsh = 0.8
    cacheplusweb = cacheplusweb(env,bs1,nm1,st1,bs2,nm2,st2,tsh)

    # start the arrival process
    env.process(car_arrival.arrival_process(cacheplusweb))

    # simulate until SIM_TIME
    env.run(until=SIM_TIME)



    fig,(rt1,rt2,tot) = pyplot.subplots(3,1)
    rt1.plot(cacheplusweb.response_time1)
    rt1.set_ylabel('RT1')
    rt2.set_ylabel('RT2')
    rt2.plot(cacheplusweb.response_time2)
    tot.plot(cacheplusweb.total_response_time)
    tot.set_ylabel('TOT')

    fig, (bo1,bo2) = pyplot.subplots(2,1)
    bo1.plot(cacheplusweb.bo1)
    bo2.plot(cacheplusweb.bo2)
    bo1.set_ylabel('BO1')
    bo2.set_ylabel('BO2')
    pyplot.show()




