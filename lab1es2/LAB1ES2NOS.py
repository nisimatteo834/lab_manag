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
RANDOM_SEED = 52
INTER_ARRIVAL = 22
SERVICE_TIME = 10   # todo put it to 1 in order to have a good plot
NUM_MACHINES = 1
BUFFER_SIZE = 5
MIN_BATCH = 1
MAX_BATCH = 8
SIM_TIME = 2000



# **********************************************************************************************************************
# Packet arrival management
# **********************************************************************************************************************
class Arrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time
        # the environment
        self.env = environ
        self.totalPackets = 0
        self.packetstosend = []

    # execute the process
    def arrival_process(self, cacheplusweb):
        while True:                             # never exit the loop

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            number_packets = numpy.random.uniform(MIN_BATCH,MAX_BATCH,1).__int__()

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            print ('At', self.env.now, 'enter', number_packets, 'packets')
            # all the packets of the batches are dealt at the same time
            for x in range(0,number_packets):
                # a car has arrived - request cacheplusweb to do its job
                self.totalPackets += 1
                p = Packet(self.totalPackets)
                self.packetstosend.append(p)
                print (p.getId(),' enters at ',self.env.now)

            self.env.process(cacheplusweb.frontEnd(self.packetstosend))



class Packet():
    def __init__(self,id):
        self.id = id

    def getId(self):
        return self.id
# **********************************************************************************************************************
# Web Cache and Web server - Users performs requests that can be simultaneous (batches). in the content is in the cache
#       the service is done, otherwise the request goes to the slower web server
# **********************************************************************************************************************


class cachePlusWeb(object):

    # constructor
    def __init__(self, env, bs1, nm1, st1, bs2, nm2, st2, tsh):

        # probability threshold for a packet to go to the back server
        self.tsh = tsh

        # buffer size of web cache
        self.bs1 = bs1

        # service time of web cache
        self.st1 = st1
        self.service_time1 = 0

        # number of machines
        self.nm1 = nm1

        #buffer size of web server
        self.bs2 = bs2

        #number of web servers
        self.nm2 = nm2

        #service time of web server
        self.st2 = st2
        self.service_time2 = 0


        #
        self.machines1 = simpy.Resource(env, nm1)
        self.machines2 = simpy.Resource(env,nm2)

        # the environment
        self.env = env

        # number of cars in the shop
        self.q_memory = []

        #Queues are used to process the packets in order, as a real buffer
        self.queue1 = Queue.Queue()
        self.queue2 = Queue.Queue()

        # to keep trace of the response time, of front server, back server and total system
        self.response_time1 = []
        self.response_time2 = []
        self.total_response_time = []

        # to keep trace of the buffer occupancy
        self.bo1 = []
        self.bo2 = []


        #Counter for the dropped packets
        self.numberPacketDroppedFront = 0
        self.numberPacketDroppedBack = 0

    # Web Cache
    def frontEnd(self,packetreceived):

        for x in range(0, len(packetreceived)):
            if  (self.queue1.qsize()< self.bs1): # If there is still some buffer empty, add the packet to the queue
                self.queue1.put(packetreceived[0])
                print ('Packet ',packetreceived[0].getId(),'in Q1 at ',self.env.now)
                packetreceived.remove(packetreceived[0])
            else:
                print ('Packet ',packetreceived[0].getId(),'has been dropped by Q1 ',self.env.now)
                packetreceived.remove(packetreceived[0])
                self.numberPacketDroppedFront += 1
        # when the buffer queue is updated, save the buffer occupancy in the ad hoc vector
        self.bo1.append(self.queue1.qsize())
        print("Packets in queue1: ", self.queue1.qsize())

        while not self.queue1.empty():
            enter = self.env.now
            # request the cache to process a new packet
            with self.machines1.request() as request:
                yield request
                # once the machine is free, wait until service is finished
                self.service_time1 = random.expovariate(lambd=1.0/self.st1)
                packetserved = self.queue1.get()
                print ('Packet ', packetserved.getId(), 'served by Q1 at', self.env.now, 'should end at', self.env.now + self.service_time1)
                # yield an event to the simulator
                yield self.env.timeout(self.service_time1)

            print ('Packet ', packetserved.getId(), 'exits from FrontEnd at ', self.env.now)
            # release the  cache
            self.response_time1.append(self.env.now-enter)

            # extract a uniform random value between 0 and 1
            p = numpy.random.uniform(0,1)

            # if this value is below the threshold, the packet goes to the backEnd server
            if p <= tsh:
                 (self.env.process(self.backEnd(packetserved))) #todo yield fa casino
            else:               # otherwise the packet request is accomplished only by the cache
                self.response_time2.append(0)
                print ('packet', packetserved.getId(), 'is done')

            self.total_response_time.append(self.env.now-enter)

    # Web server
    def backEnd(self, packetreceived):
        # if there is still some space in the web server buffer add a packet to the queue
        if self.queue2.qsize() < self.bs2:
            self.queue2.put(packetreceived)
            print ('Packet ',packetreceived.getId(),'in Q2 at ', self.env.now)
        # otherwise discard it
        # after setting the queue, update queue length
        else:
            print ('Packet ',packetreceived,'has been dropped by Q2 ',self.env.now)
            self.numberPacketDroppedBack += 1

        self.bo2.append(self.queue2.qsize())

        print("Packets in buffer2: ", self.queue2.qsize())

        while not self.queue2.empty():
            enter = self.env.now
        # request the server to process the packet
            with self.machines2.request() as request:
                yield request
                # print (packetreceived.getId(), 'is asking for resource2', request)
                # yield request
                # print (packetreceived.getId(), 'is using the resource2', request)
                self.service_time2 = random.expovariate(lambd=1.0/self.st2)
                packetserved2 = self.queue2.get()
                #todo sto cambiando sotto

                print (packetserved2.getId(), 'is asking for resource2', request)
                print (packetserved2.getId(),self.service_time2,self.env.now+self.service_time2)
                print (packetserved2.getId(), 'is using the resource2', request)

                #todo finqua

                # once the machine is free, wait until service is finished

                print ('Packet ', packetserved2.getId(), 'served in Q2 at', self.env.now, 'shold end at', self.env.now + self.service_time2)
                # yield an event to the simulator
                yield self.env.timeout(self.service_time2)


            print ('Packet ', packetserved2.getId(), 'end in Q2 at', self.env.now)
            # release the back server
            self.response_time2.append(self.env.now-enter)
            print ('prova', self.queue2.qsize())


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

    # packet batch arrival
    packet_arrival = Arrival(env, INTER_ARRIVAL)

    # cacheplusweb
    bs1 = BUFFER_SIZE
    bs2 = BUFFER_SIZE
    nm1 = NUM_MACHINES
    nm2 = NUM_MACHINES
    st1 = SERVICE_TIME/10
    st2 = SERVICE_TIME
    tsh = 0.7
    cacheplusweb = cachePlusWeb(env, bs1, nm1, st1, bs2, nm2, st2, tsh)

    # start the arrival process
    env.process(packet_arrival.arrival_process(cacheplusweb))

    # simulate until SIM_TIME
    env.run(until=SIM_TIME)

    ##########################
    #      Statistics        #
    ##########################

    print ('Dropped packets in Front Server', cacheplusweb.numberPacketDroppedFront )
    print ('Dropped packets in Back Server', cacheplusweb.numberPacketDroppedBack)

    fig, (rt1, rt2, tot) = pyplot.subplots(3, 1)
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




