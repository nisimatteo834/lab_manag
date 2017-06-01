import simpy
import random
import numpy
from matplotlib import pyplot
from process import  Buffer
from packetarrival import PacketArrival

RANDOM_SEED = 42
INTER_ARRIVAL = 25
SERVICE_TIME = 1
NUM_MACHINES = 1
SIM_TIME = 100000

if __name__ == '__main__':

    random.seed(RANDOM_SEED)


    theoretical_buffer_occupancy = []
    average_buffer_occupancy = []
    average_response_time = []
    theoretical_response_time = []
    ro_vector = []

    #With this for loop, we make increasing the service time and as a consequence rho in order to evaluate how the system
    #reacts to this increasing
    for x in range(SERVICE_TIME,INTER_ARRIVAL,1):
        env = simpy.Environment()
        packet_arrival = PacketArrival(env, INTER_ARRIVAL)
        buffer = Buffer(env, NUM_MACHINES, x)

        # start the arrival process
        env.process(packet_arrival.arrival_process(buffer))

        # simulate until SIM_TIME
        env.run(until=SIM_TIME)

        #here we save one of the simulation, for instance one with a great rho.
        #
        if (x==SERVICE_TIME):
            occupancy_for_hist_little_rho = buffer.q_memory

        if (x==INTER_ARRIVAL-1):
            occupancy_for_hist_big_rho = buffer.q_memory
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

    fig,(big,little) = pyplot.subplots(2,1)
    fig.text(0.5, 0.04, 'Number of packets in the buffer', ha='center', va='center')
    fig.text(0.04, 0.5, 'Occurences', ha='center', va='center', rotation='vertical')
    big.hist(occupancy_for_hist_big_rho,label='Histogram with rho about 1')
    little.hist(occupancy_for_hist_little_rho,label='Histogram with rho about 1')
    handles,labels = big.get_legend_handles_labels()
    big.legend(handles,labels)
    handles,labels = little.get_legend_handles_labels()
    little.legend(handles,labels)

    pyplot.show()
