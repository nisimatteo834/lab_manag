import simpy
import random
import numpy
from decimal import Decimal
from matplotlib import pyplot
from process import  Buffer
from packetarrival import PacketArrival

RANDOM_SEED = 42
INTER_ARRIVAL = 25
SERVICE_TIME = 1
NUM_MACHINES = 1
SIM_TIME = 100000000

if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    # ********************************
    # setup and perform the simulation
    # ********************************

    theoretical_buffer_occupancy = []
    average_buffer_occupancy = []
    average_response_time = []
    theoretical_response_time = []
    ro_vector = []

    for x in range(SERVICE_TIME,INTER_ARRIVAL,1):
        env = simpy.Environment()
        packet_arrival = PacketArrival(env, INTER_ARRIVAL)
        buffer = Buffer(env, NUM_MACHINES, x)

        # start the arrival process
        env.process(packet_arrival.arrival_process(buffer))

        # simulate until SIM_TIME
        env.run(until=SIM_TIME)

        if (x==INTER_ARRIVAL-1):
            occupancy_for_hist = buffer.q_memory
        average_response_time.append(numpy.mean(buffer.response_time))
        theoretical_response_time.append(float(1)/(float(1)/x-float(1)/INTER_ARRIVAL))

        average_buffer_occupancy.append(numpy.mean(buffer.q_memory))
        theoretical_buffer_occupancy.append(theoretical_response_time[-1]/INTER_ARRIVAL)
        ro = float(x)/INTER_ARRIVAL
        ro_vector.append(ro)


    print ('AVG BUFFER OCCUPANCY',average_buffer_occupancy)
    print ('TH BUFFER OCCUPANCY', theoretical_buffer_occupancy)
    print ('AVG RESPONSE TIME',average_response_time)
    print ('TH RESPONSE TIME', theoretical_response_time)

    fig, (buff, resp) = pyplot.subplots(2,1)
    buff.plot(ro_vector,average_buffer_occupancy,label='AVG BUFF')
    buff.plot(ro_vector,theoretical_buffer_occupancy,label='TH BUFF')

    handles, labels = buff.get_legend_handles_labels()
    buff.legend(handles, labels)


    resp.plot(ro_vector,average_response_time,label='AVG RESP')
    resp.plot(ro_vector,theoretical_response_time,label='TH RESP')

    handles, labels = resp.get_legend_handles_labels()
    resp.legend(handles, labels)

    pyplot.figure(2)
    pyplot.hist(occupancy_for_hist)

    pyplot.figure(3)
    pyplot.plot(occupancy_for_hist)

    pyplot.show()
