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
SIM_TIME = 3000



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
                print (self.totalPackets, ' enters at ', self.env.now)
                self.env.process(cacheplusweb.frontEnd(self.totalPackets))


class cachePlusWeb(object):

    # constructor
    def __init__(self, env, bs1, nm1, st1, bs2, nm2, st2, tsh):

        self.qFront = 0
        self.qBack = 0


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
        self.queue1 = 0
        self.queue2 = 0

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
        self.qFront +=1
        enter = self.env.now
        if self.qFront > self.bs1:
            print ('Packet',packetreceived,'dropped')
            self.numberPacketDroppedFront += 1
            self.qFront -=1
            self.bo1.append(self.qFront)

        else:
            with self.machines1.request() as request1:
                self.bo1.append(self.qFront)
                print ('Packet',packetreceived,'in Q1 asks for',request1,self.env.now)
                yield request1
                print ('Packet',packetreceived,'obtains',request1,self.env.now)
                yield self.env.timeout(random.expovariate(lambd=1.0/self.st1))
                print ('Packet',packetreceived,'releases in Q1',request1,self.env.now)
            self.qFront -= 1
            self.response_time1.append(self.env.now - enter)
            self.bo1.append(self.qFront)



            p = numpy.random.uniform(0, 1)

            if p <= tsh:
                self.qBack +=1
                if self.qBack > self.bs2:
                    print (packetreceived,'dropped in Q2')
                    self.numberPacketDroppedBack +=1
                    self.qBack -=1
                    self.bo2.append(self.qBack)
                else:
                    print (packetreceived, 'enters Q2 at', self.env.now)
                    self.bo2.append(self.qBack)
                    enter2 = self.env.now
                    with self.machines2.request() as request2:
                        print (packetreceived, 'in Q2 is asking for', request2)
                        yield request2
                        print(packetreceived, 'in Q2 has obtained', request2,self.env.now)
                        service = random.expovariate(lambd=1.0 / self.st2)
                        print (service)
                        yield self.env.timeout(service)
                        print (packetreceived, 'in Q2 releases', request2,self.env.now)
                    self.qBack -= 1
                    self.bo2.append(self.qBack)
                    self.response_time2.append(self.env.now - enter2)

            else:
                self.response_time2.append(0)

            self.total_response_time.append(self.env.now-enter)


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
    st2 = SERVICE_TIME*10
    tsh = 0.9999999
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




