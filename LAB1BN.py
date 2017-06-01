#!/usr/bin/python3

import simpy
import random
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
SERVICE_TIME = 1#todo put it to 1 in order to have a good plot
NUM_MACHINES = 1
MAX_BATCH = 10
SIM_TIME = 100000
MIN_BATCH = 1
BUFFER_SIZE = 5

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
    def arrival_process(self, carwash):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            number_packets = numpy.random.uniform(MIN_BATCH,MAX_BATCH,1).__int__()

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            #print ('At', self.env.now, 'enter', number_packets, 'packets')

            for x in range(0,number_packets):
                # a car has arrived - request carwash to do its job
                self.count += 1
                p = Packet(self.count)
                self.packetstosend.append(p)
                #print (p.getId(),' enters at ',self.env.now)
            self.env.process(carwash.wash(self.packetstosend))


class Packet():
    def __init__(self,id):
        self.id = id

    def getId(self):
        return self.id
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
    rho_vector = []
    packetDroppedForSimulation = []
    dropOccurrence = []
    totalPacket = []
    testrun = []
    loose_prob = []

    #todo scegliere come far variare il buffer size o il max batch per valutare

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


        average_response_time.append(numpy.mean(carwash.response_time))
#        theoretical_response_time.append(float(1)/(float(1)/x-float(1)/INTER_ARRIVAL))

        average_buffer_occupancy.append(numpy.mean(carwash.q_memory))
 #       theoretical_buffer_occupancy.append(theoretical_response_time[-1]/INTER_ARRIVAL)
        s_t_vector.append(x)
        rho_vector.append(x/INTER_ARRIVAL)
        packetDroppedForSimulation.append(carwash.numberPacketDropped)

        #TODO TRYING THEROETICAL BUFFER OCCUPANCY
        rho = float(x)/INTER_ARRIVAL
        loose_prob.append((MAX_BATCH+MIN_BATCH/2)*(1-rho)*(numpy.power(rho,BUFFER_SIZE))/(1-numpy.power(rho,BUFFER_SIZE+1)))

        totalPacket.append(car_arrival.count)
        dropOccurrence.append(float(carwash.numberPacketDropped)/car_arrival.count)
        if (x==2):
            testrun = carwash.response_time


    print ('AVG BUFFER OCCUPANCY',average_buffer_occupancy)
    print ('TH BUFFER OCCUPANCY', theoretical_buffer_occupancy)
    print ('AVG RESPONSE TIME',average_response_time)
    print ('TH RESPONSE TIME', theoretical_response_time)
    print ('PACKET DROPPED COMPUTED ', packetDroppedForSimulation)
    print ('TOTAL PACKET ', totalPacket)
    print ('DROP OCCURRENCES', dropOccurrence)

    confidence_interval = 0.90*average_response_time[1]
    flag = 1
    end_tran = 0
    a = 0
    for a in range(0,len(testrun),10):
        media = numpy.mean(testrun[a:a+10])
        if (media > confidence_interval):
            flag = a+10
            break


    print ('MEAN OF ALL THE VECTOR',numpy.mean(testrun))
    print ('MEAN OF VECOTR WITHOUT TRANSIENT',numpy.mean(testrun[flag:-1]))
    print ('MEAN OF THE TRANSIENT',numpy.mean(testrun[0:flag]))
    print ('CONFIDENCE INTERVAL',confidence_interval)
    print (average_response_time[2])

    pyplot.plot(testrun)



    fig, (buff, resp) = pyplot.subplots(2,1)
    buff.plot(s_t_vector,average_buffer_occupancy,label='AVG BUFF')
    handles, labels = buff.get_legend_handles_labels()
    buff.legend(handles, labels)


    resp.plot(s_t_vector,average_response_time,label='AVG RP')
    handles, labels = resp.get_legend_handles_labels()
    resp.legend(handles, labels)

    fig, (drop,ratio) = pyplot.subplots(2,1)

    #ratio.plot(loose_prob,label='LOOSE PROB')

    drop.plot(s_t_vector,packetDroppedForSimulation,label='PACKET DROPPED')
    ratio.plot(s_t_vector,dropOccurrence,label='DROP OCC')
    handles, labels = drop.get_legend_handles_labels()
    drop.legend(handles, labels)
    handles, labels = ratio.get_legend_handles_labels()
    ratio.legend(handles, labels)

    pyplot.show()


#todo cancella buff e rt theoretical








