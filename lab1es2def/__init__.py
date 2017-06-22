
import simpy
import numpy
from decimal import Decimal
from matplotlib import pyplot
import random
import Queue
from CachePlusWeb import cachePlusWeb
from Arrival import Arrival

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 52
INTER_ARRIVAL = 22
SERVICE_TIME = 10   # todo put it to 1 in order to have a good plot
NUM_MACHINES = 1
BUFFER_SIZE = 10
MIN_BATCH = 1
MAX_BATCH = 8
SIM_TIME = 3000




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
    packet_arrival = Arrival(env, INTER_ARRIVAL, MIN_BATCH, MAX_BATCH)

    # cacheplusweb
    bs1 = BUFFER_SIZE
    bs2 = BUFFER_SIZE
    nm1 = NUM_MACHINES
    nm2 = NUM_MACHINES
    st1 = SERVICE_TIME/10
    st2 = SERVICE_TIME*10
    tsh = 2
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