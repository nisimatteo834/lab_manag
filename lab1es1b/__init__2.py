#!/usr/bin/python3

import simpy
import numpy
from matplotlib import pyplot
import random
from packet import Packet
from service2 import Service
from arrival2 import PacketArrival

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 48
INTER_ARRIVAL = 15
SERVICE_TIME = 1
NUM_MACHINES = 1
SIM_TIME = 100000


if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    theoretical_buffer_occupancy = []
    average_buffer_occupancy = []
    average_buffer_occupancy.append(0)
    average_response_time = []
    theoretical_response_time = []
    s_t_vector = []
    rho_vector = []
    rho_vector.append(0)
    packetDroppedForSimulation = []
    packetDroppedForSimulation.append(0)
    dropOccurrence = []
    totalPacket = []
    testrun = []
    loose_prob = []

    for x in range(SERVICE_TIME,INTER_ARRIVAL+1,1):
        env = simpy.Environment()

        packet_arrival = PacketArrival(env, INTER_ARRIVAL)
        service = Service(env, NUM_MACHINES, x)

        env.process(packet_arrival.arrival_process(service))
        env.run(until=SIM_TIME)


        average_response_time.append(numpy.mean(service.response_time))
        average_buffer_occupancy.append(numpy.mean(service.q_memory))
        s_t_vector.append(x)
        rho_vector.append(float(x)/INTER_ARRIVAL)
        packetDroppedForSimulation.append(service.numberPacketDropped)

        rho = float(x)/INTER_ARRIVAL

        totalPacket.append(packet_arrival.count)
        dropOccurrence.append(float(service.numberPacketDropped)/packet_arrival.count)


    print ('AVG BUFFER OCCUPANCY',average_buffer_occupancy)
    print ('AVG RESPONSE TIME',average_response_time)
    print ('PACKET DROPPED COMPUTED ', numpy.mean(packetDroppedForSimulation))
    print ('DROP OCCURRENCES', numpy.mean(dropOccurrence))

    fig, (drop,ratio) = pyplot.subplots(2,1)
    drop.plot(rho_vector,packetDroppedForSimulation,label='PACKETS DROPPED')
    ratio.plot(rho_vector,average_buffer_occupancy,label = 'AVG B.O.')
    handles, labels = drop.get_legend_handles_labels()
    drop.legend(handles, labels)
    handles, labels = ratio.get_legend_handles_labels()
    ratio.legend(handles, labels)

    pyplot.show()
