import simpy
import random
from matplotlib import pyplot

class Arrival(object):

    def __init__(self, environment, arrivalRate, minBatch, maxBatch):

        # store all  intervals between arrivals that are generated
        self.interArrival = []

        # arrival rate
        self.arrivalRate = arrivalRate

        # environment
        self.env = environment

        # parameters for the uniform distribution used in batch
        self.minBatch = minBatch
        self.maxBatch = maxBatch

        # store the number of arrivals at once
        self.batch = []


    def arrival(self, service):

        while True:

            # sample the time to the next arrival
            self.interArrival.append(random.expovariate(lambd=1.0/self.arrivalRate))

            # sample the number of packets that will arrive at the same time
            self.batch.append(random.uniform(self.minBatch, self.maxBatch))

            # wait for time defined by interArrival
            yield self.env.timeout(self.interArrival[-1])

            print "At instant ", self.env.now, "the number of packets arriving is ", int(self.batch[-1])

            # call the process many times (= number of packets arriving at the same time)
            for i in range(0, int(self.batch[-1])):
                self.env.process(service.job())


class Service(object):

    def __init__(self, environment, serviceRate1, numServer1, bufSize1, serviceRate2, numServer2, bufSize2, probP):

        # environment
        self.env = environment

        # service rate
        self.serviceRate1 = serviceRate1
        self.serviceRate2 = serviceRate2

        # number of servers
        self.frontServers = simpy.Resource(self.env, numServer1)
        self.backServers = simpy.Resource(self.env, numServer2)

        # queue size
        self.q1 = 0
        self.q2 = 0

        # buffer size
        self.bufSize1 = bufSize1
        self.bufSize2 = bufSize2

        # probability of staying in the system
        self.tresholdP = probP

        # count number of packets arriving
        self.countJob1 = 0
        self.countJob2 = 0

        # count dropped packets
        self.countDropped1 = 0
        self.countDropped2 = 0

        # store time to complete the job
        self.jobTime1 = []
        self.jobTime2 = []

        # starting time
        self.startTime1 = []
        self.startTime2 = []

        # ending time
        self.endTime1 = []
        self.endTime2 = []



    def job(self):

        # increment the front end queue size - one packet arrived
        # TODO self.q1 += 1

        # TODO print "Packets in the Front Server buffer: ", self.q1 #TODO NON e' VERO! DA CAMBIARE!

        # check if the buffer 1 is full

        # buffer 1 full - drop packet and decrease queue 1 size
        if self.q1 + 1 > self.bufSize1:
            print "Packet dropped in Front Server at: ", self.env.now
            # TODO self.q1 -= 1
            # TODO self.countDropped1 += 1
            print "Packets in the Front Server buffer: ", self.q1

        # buffer 1 not full - proceed with request
        else:
            # I'm before the buffer request a server to do the job
            self.q1 += 1
            # starting time - front end
            with self.frontServers.request() as request:
                yield request

                # start the job
                print "Service has started in Front Server at time: ", self.env.now

                # packet that is being served is removed from buffer

                # sample the time needed to complete the job in front server

                self.startTime1.append(self.env.now)
                self.jobTime1.append(random.expovariate(lambd=1.0/self.serviceRate1))
                # yield an event to the simulator
                yield self.env.timeout(self.jobTime1[-1])

                # stores the instant when the job in front server was done
                self.endTime1.append(self.env.now)

                self.q1 -= 1
                print "Packets in the Front Server buffer: ", self.q1 #TODO DA SPOSTARE ANCHE QUESTO COME SU

                self.countJob1 += 1
                print "Service of packet no. %d done in Front Server at: %f" % (self.countJob1, self.env.now)

        # generates a value from 0 to 1 to evaluate if packet goes to back server
        p = random.uniform(0, 1)
        print "Probability p: ", p

        # packet goes to back server
        if p > self.tresholdP:

            # increment the queue size - one packet arrived
            self.q2 += 1

            print "Packets in the Back Server buffer: ", self.q2

            # check if the buffer is full

            # buffer full - drop packet and decrease queue size
            if self.q2 + 1 > self.bufSize2:
                print "Packet dropped in Back Server at: ", self.env.now
                # self.q2 -= 1
                # self.countDropped2 += 1
                print "Packets in the Back Server buffer: ", self.q2

            # buffer not full - proceed with request
            else:
                # I'm before the buffer request a server to do the job
                self.q2 += 1
                self.startTime2.append(self.env.now)

                with self.backServers.request() as request:
                    yield request

                    # start the job
                    print ("Service has started in Back Server at time: ", self.env.now)

                    # packet that is being served is removed from buffer

                    # sample the time needed to complete the job
                    self.jobTime2.append(random.expovariate(lambd=1.0 / self.serviceRate2))

                    # yield an event to the simulator
                    yield self.env.timeout(self.jobTime2[-1])

                    # stores the instant when the job in back server was done
                    self.endTime2.append(self.env.now)

                    self.q2 -= 1
                    print ("Packets in the Back Server buffer: ", self.q2)

                    # increment the counter to choose the correct time to finish the job
                    self.countJob2 += 1

                    print "Service of packet no. %d done in Back Server at: %f" % (self.countJob2, self.env.now)



# Arrival
ARRIVAL_RATE = 9
MIN_BATCH = 1
MAX_BATCH = 5

# Front-end server
SERVICE_RATE_1 = 7
NUM_SERVERS_1 = 1
BUFFER_SIZE_1 = 15

# Back-end server
SERVICE_RATE_2 = 7
NUM_SERVERS_2 = 1
BUFFER_SIZE_2 = 15
PROBABILITY_P = 0.5

# Simulation
RANDOM_SEED = 42
SIM_TIME = 50


###########################################
# Main - One experiment
###########################################

if __name__ == "__main__":

    # Seed
    random.seed(RANDOM_SEED)

    # creates environment
    env = simpy.Environment()

    # initializes arrivals in front-end server
    packetFront = Arrival(env, ARRIVAL_RATE, MIN_BATCH, MAX_BATCH)

    # initializes front-end server
    server = Service(env, SERVICE_RATE_1, NUM_SERVERS_1, BUFFER_SIZE_1, SERVICE_RATE_2, NUM_SERVERS_2, BUFFER_SIZE_2, PROBABILITY_P)

    # initialize back-end server
    # backServer = Service(env, SERVICE_RATE_2, NUM_SERVERS_2, BUFFER_SIZE_2)

    # starts the arrival process in the front server
    env.process(packetFront.arrival(server))

    # simulates until SIM_TIME
    env.run(until=SIM_TIME)

    #################
    # Statistics
    #################

    # packets dropped in front server
    print "Number of packets dropped in front-end server: ", server.countDropped1

    # packets dropped in back server
    print "Number of packets dropped in back-end server: ", server.countDropped2



    print ('E1',server.endTime1)
    print ('S1',server.startTime1)
    print ('J1',server.jobTime1)
    print ('E2',server.endTime2)
    print ('S2',server.startTime2)
    print ('J2',server.jobTime2)
    #print (server.endTime2)

    # response time - front server
    responseTime1 = []
    for i in range(len(server.endTime1)):
        responseTime1.append(server.endTime1[i] - server.startTime1[i])

    # response time - back server
    responseTime2 = []
    for i in range(len(server.endTime2)):
        responseTime2.append(server.endTime2[i] - server.startTime2[i])

    # response time - total
    responseTime = []
    for i in range(len(server.endTime2)):
        responseTime.append(server.endTime2[i] - server.startTime1[i])
        print (server.endTime2[i] - server.startTime1[i])

    # response time plot
    fig1, (response1, response2, responseT) = pyplot.subplots(3, 1)

    response1.plot(responseTime1)
    response1.set_xlabel("Sample")
    response1.set_ylabel("Front Server Response Time")

    response2.plot(responseTime2)
    response2.set_xlabel("Sample")
    response2.set_ylabel("Back Server Response Time")

    responseT.plot(responseTime)
    responseT.set_xlabel("Sample")
    responseT.set_ylabel("Total Response Time")

    # inter arrival plot
    #fig2,

    pyplot.show()



