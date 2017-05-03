import simpy
import random
import numpy
from matplotlib import pyplot
import math


class Arrival(object):

    def __init__(self, environment, arrivalRate, minBatch, maxBatch):

        # store all  intervals between arrivals that are generated
        self.interArrival = []

        # arrival rate
        self.arrivalRate = arrivalRate

        # environment
        self.env = environment

        # counter to choose the inter-arrival
        self.count = 0

        self.minBatch = minBatch
        self.maxBatch = maxBatch
        self.batch = []

    #    self.arrivalTime = []

    def arrival(self, service):

        while True:

            interval = random.expovariate(lambd=1.0/self.arrivalRate)
            self.batch.append(random.uniform(self.minBatch, self.maxBatch))


            self.interArrival.append(interval)
            yield self.env.timeout(self.interArrival[self.count])
            print "A no. of", int(self.batch[-1]), "packets have arrived at ", self.env.now
            self.count +=1

            for i in range(0, int(self.batch[-1])):
                self.env.process(service.job())

class Service(object):

    def __init__(self, environment, serviceRate, numServer, bufSize):

        # environment
        self.env = environment

        # service rate
        self.serviceRate = serviceRate

        # number of servers
        self.servers = simpy.Resource(self.env, numServer)

        # store time to complete the job
        self.jobTime = []

        # counter to choose the time to complete a job
        self.count = 0

        # queue size
        self.qsize = 0

        self.bufSize = bufSize

        self.startTime = []
        self.endTime = []
        self.dropCount = 0


    def job(self):

        self.qsize += 1
        print "Packets in the buffer: ", self.qsize

        if self.qsize > self.bufSize :
            print "Packet dropped."
            self.qsize -= 1
            self.dropCount += 1
        else :
            #I'm before the buffer, request a server to do the job
            self.startTime.append(self.env.now)
            with self.servers.request() as request:
                print (request)
                yield request

                print "Service has started at time: ", self.env.now
                self.qsize -= 1

                self.jobTime.append(random.expovariate(lambd=1.0/self.serviceRate))

                # yield an event to the simulator
                yield self.env.timeout(self.jobTime[self.count])

                self.count+=1
                self.endTime.append(self.env.now)
                print "Service of packet no. %d done at: %f" % (self.count, self.env.now)

if __name__ == "__main__":

    ARRIVAL_RATE = 11.1
    SERVICE_RATE = 0.1  # make it change!
    NUM_SERVERS = 3

    RANDOM_SEED = 42
    SIM_TIME = 10000

    MIN_BATCH = 2
    MAX_BATCH = 5
    BUFFER_SIZE = 30

    meanJob = []  # average response time
    rho = []
    theoryResponse = []
    bufferOccupancy = []
    theoryBuffer = []
    droppedPackets = []
    # Seed
    # random.seed(RANDOM_SEED)

    for i in range(50):
        SERVICE_RATE = SERVICE_RATE + 0.2
        # creates Environment
        env = simpy.Environment()
        # initializes arrivals
        packet = Arrival(env, ARRIVAL_RATE, MIN_BATCH, MAX_BATCH)

        # initializes service
        service = Service(env, SERVICE_RATE, NUM_SERVERS, BUFFER_SIZE)

        # starts the arrival process
        env.process(packet.arrival(service))

        # simulates until SIM_TIME
        env.run(until=SIM_TIME)

        # print "End time is: ", service.endTime
        # print "Start time is: ", service.startTime

        responseTime = []
        for m in range(len(service.endTime)):
            responseTime.append(service.endTime[m] - service.startTime[m])

        rho.append(SERVICE_RATE / ARRIVAL_RATE)

        meanJob.append(numpy.mean(responseTime))  # do the same for buffer!
        theoryResponse.append(1.0 / (1.0 / SERVICE_RATE - 1.0 / ARRIVAL_RATE))

        bufferOccupancy.append(numpy.mean(service.qsize))
        theoryBuffer.append(
            math.pow(SERVICE_RATE / ARRIVAL_RATE, 2) / (1.0 - SERVICE_RATE / ARRIVAL_RATE))  # E[Nw] - only buffer

        droppedPackets.append(service.dropCount)

        # print "Rho: ", rho

    print "Response time is: ", responseTime
    print "Dropped packets: ", droppedPackets

    # plotting
    fig, (resptime, buffocc, drop) = pyplot.subplots(3, 1)
    resptime.plot(rho, meanJob, rho, theoryResponse, 'g', linewidth=2.0)
    resptime.set_xlabel("rho")
    resptime.set_ylabel("Response time")
    # resptime.legend('Simulation response time', 'Theoretical response time')

    buffocc.plot(rho, bufferOccupancy, rho, theoryBuffer, 'g', linewidth=2.0)
    buffocc.set_xlabel("rho")
    buffocc.set_ylabel("Buffer occupancy")

    drop.plot(rho, droppedPackets, linewidth=2.0)
    drop.set_xlabel("rho")
    drop.set_ylabel("Dropped packets")

    pyplot.show()
