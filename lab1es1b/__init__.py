#!/usr/bin/python3

import simpy
import numpy
from matplotlib import pyplot
import random
from packet import Packet
from service import Service
from arrival import PacketArrival

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 50
INTER_ARRIVAL = 15
SERVICE_TIME = 1
NUM_MACHINES = 1
MAX_BATCH = 10
SIM_TIME = 10000000
MIN_BATCH = 1
BUFFER_SIZE = 5


if __name__ == '__main__':

    random.seed(RANDOM_SEED)

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

    for x in range(SERVICE_TIME,INTER_ARRIVAL,1):
        env = simpy.Environment()

        packet_arrival = PacketArrival(env, INTER_ARRIVAL)
        service = Service(env, NUM_MACHINES, x)

        env.process(packet_arrival.arrival_process(service))
        env.run(until=SIM_TIME)


        average_response_time.append(numpy.mean(service.response_time))
        average_buffer_occupancy.append(numpy.mean(service.q_memory))
        s_t_vector.append(x)
        rho_vector.append(x/INTER_ARRIVAL)
        packetDroppedForSimulation.append(service.numberPacketDropped)

        rho = float(x)/INTER_ARRIVAL

        totalPacket.append(packet_arrival.count)
        dropOccurrence.append(float(service.numberPacketDropped)/packet_arrival.count)
        if (x==2):
            testrun = service.response_time


    print ('AVG BUFFER OCCUPANCY',average_buffer_occupancy)
    print ('AVG RESPONSE TIME',average_response_time)
    print ('PACKET DROPPED COMPUTED ', packetDroppedForSimulation)
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


    resp.plot(s_t_vector,average_response_time,label='AVG RT')
    handles, labels = resp.get_legend_handles_labels()
    resp.legend(handles, labels)

    fig, (drop,ratio) = pyplot.subplots(2,1)

    drop.plot(s_t_vector,packetDroppedForSimulation,label='PACKETS DROPPED')
    ratio.plot(s_t_vector,dropOccurrence,label='DROP OCC')
    handles, labels = drop.get_legend_handles_labels()
    drop.legend(handles, labels)
    handles, labels = ratio.get_legend_handles_labels()
    ratio.legend(handles, labels)

    pyplot.show()
