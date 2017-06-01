import simpy
import random
import numpy
from matplotlib import pyplot
from Arrival import Arrival
from Service import Service

# Arrival
ARRIVAL_RATE = 5
MIN_BATCH = 1
MAX_BATCH = 8


# Front-end server
SERVICE_TIME_1 = 10
NUM_SERVERS_1 = 1
BUFFER_SIZE_1 = 10

# Back-end server
SERVICE_TIME_2 = 20
NUM_SERVERS_2 = 1
BUFFER_SIZE_2 = 10
PROBABILITY_P = 0.8

# Simulation
RANDOM_SEED = 42
SIM_TIME = 10000



###########################################
# Main - One experiment
###########################################

if __name__ == "__main__":
    # for cacheServerFactor in [2, 5, 10, 20]:

    meanRT1 = []
    meanRT2 = []
    meanRT = []
    meanBO1 = []
    meanBO2 = []

    for p in range(0,10):
        print ('round', p)


        # Seed
        random.seed(RANDOM_SEED)

        # creates environment
        env = simpy.Environment()

        # initializes arrivals in front-end server
        packetFront = Arrival(env, ARRIVAL_RATE, MIN_BATCH, MAX_BATCH)

        # initializes front-end server
        server = Service(env, SERVICE_TIME_1, NUM_SERVERS_1, BUFFER_SIZE_1, SERVICE_TIME_2, NUM_SERVERS_2, BUFFER_SIZE_2, p/10)

        # initialize back-end server
        # backServer = Service(env, SERVICE_RATE_2, NUM_SERVERS_2, BUFFER_SIZE_2)

        # starts the arrival process in the front server
        env.process(packetFront.arrival(server))

        # simulates until SIM_TIME
        env.run(until=SIM_TIME)

    #################
    # Statistics
    #################

    # Total number of packets


        print 'Total number of packets in the simulation: ', packetFront.totalPackets

        # packets dropped in front server
        # print "Number of packets dropped in front-end server: ", server.countDropped1

        # packets dropped in back server
        # print "Number of packets dropped in back-end server: ", server.countDropped2

        # print ('front buffer length is ', len(server.buffOcc1))
        # print ('back buffer length is ', len(server.buffOcc2))






        # response time - front server
        responseTime1 = []
        for i in range(len(server.endTime1)):
            responseTime1.append(server.endTime1[i] - server.startTime1[i])
        # print ('Mean service time S1', numpy.mean(responseTime1))
        meanRT1.append(numpy.mean(responseTime1))

        # response time - back server
        responseTime2 = []
        for i in range(len(server.endTime2)):
            responseTime2.append(server.endTime2[i] - server.startTime2[i])
        meanRT2.append(numpy.mean(responseTime2))

        # response time - total
        responseTime = []
        for i in range(len(server.endTime2)):
            responseTime.append(server.endTime2[i] - server.startTime1[i])
            # print (server.endTime2[i] - server.startTime1[i])
        meanRT.append(numpy.mean(responseTime))

        meanBO1.append(numpy.mean(server.buffOcc1))
        meanBO2.append(numpy.mean(server.buffOcc2))

    # response time plot
    fig1, (response1, response2, responseT) = pyplot.subplots(3, 1)

    response1.plot(meanRT1)
    response1.set_xlabel("Sample")
    response1.set_ylabel("Front Server Resp Time")

    response2.plot(meanRT2)
    response2.set_xlabel("Sample")
    response2.set_ylabel("Back Server Resp Time")

    responseT.plot(meanRT)
    responseT.set_xlabel("Sample")
    responseT.set_ylabel("Total Resp Time")

    # buffer occupancy plot
    fig2, (BufferFront, BufferBack) = pyplot.subplots(2,1)

    BufferFront.plot(meanBO1)
    response1.set_xlabel("Sample")
    response1.set_ylabel("Front Server Buff Occ")

    BufferBack.plot(meanBO2)
    response1.set_xlabel("Sample")
    response1.set_ylabel("Back Server Buff Occ")


    pyplot.show()