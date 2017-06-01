import simpy
import random
import numpy

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
        self.pMinusOne = 0
        self.dropped2vector = []
        self.sortedPackets = []

        # store time to complete the job
        self.jobTime1 = []
        self.jobTime2 = []

        # starting time
        self.startTime1 = []
        self.startTime2 = []

        # ending time
        self.endTime1 = []
        self.endTime2 = []

        # buffer occupancy
        self.buffOcc1 = []
        self.buffOcc2 = []




    def job(self,isLastBatchPacket):

        # increment the front end queue size - one packet arrived
        # TODO self.q1 += 1

        # TODO print "Packets in the Front Server buffer: ", self.q1 #TODO NON e' VERO! DA CAMBIARE!

        # check if the buffer 1 is full

        # buffer 1 full - drop packet and decrease queue 1 size
        if self.q1 + 1 > self.bufSize1:
            # print ("Packet dropped in Front Server at: ", self.env.now)
            # TODO self.q1 -= 1
            self.countDropped1 += 1
            # print ("Packets in the Front Server buffer: ", self.q1)
            if isLastBatchPacket:
                self.buffOcc1.append(self.q1)
                # print ('added to buffOcc1', self.q1)

        # buffer 1 not full - proceed with request
        else:
            # I'm before the buffer request a server to do the job
            self.q1 += 1
            # print ("Packets in the Front Server buffer: ", self.q1)
            if isLastBatchPacket:
                self.buffOcc1.append(self.q1)
                # print ('added to buffOcc1', self.q1)
            # starting time - front end
            with self.frontServers.request() as request:
                yield request

                # start the job
                # print ("Service has started in Front Server at time: ", self.env.now)

                # packet that is being served is removed from buffer

                # sample the time needed to complete the job in front server

                self.startTime1.append(self.env.now)
                self.jobTime1.append(random.expovariate(lambd=1.0/self.serviceRate1))
                # yield an event to the simulator
                yield self.env.timeout(self.jobTime1[-1])

                # stores the instant when the job in front server was done
                self.endTime1.append(self.env.now)

                self.q1 -= 1
                self.buffOcc1.append(self.q1)
                # print ('added to buffOcc1', self.q1)
                # print ("Packets in the Front Server buffer: ", self.q1) #TODO DA SPOSTARE ANCHE QUESTO COME SU

                self.countJob1 += 1
                # print ("Service of packet no. %d done in Front Server at: %f") % (self.countJob1, self.env.now)

        # generates a value from 0 to 1 to evaluate if packet goes to back server
        p = random.uniform(0, 1)
        # print ("Probability p: ", p)

        # packet goes to back server
        self.sortedPackets.append(self.pMinusOne)
        if p < self.tresholdP:

            # increment the queue size - one packet arrived
            if self.q2 + 1 > self.bufSize2:
                self.buffOcc2.append(self.q2)
                # print ("Packet dropped in Back Server at: ", self.env.now)
                # self.q2 -= 1
                self.countDropped2 += 1
                # print ("Packets in the Back Server buffer: ", self.q2)

            else:
                self.q2 += 1
                self.buffOcc2.append(self.q2)
                # print ("Packets in the Back Server buffer: ", self.q2)
                self.startTime2.append(self.env.now)

                with self.backServers.request() as request:
                    yield request

                    # start the job
                    # print ("Service has started in Back Server at time: ", self.env.now)

                    # packet that is being served is removed from buffer

                    # sample the time needed to complete the job
                    self.jobTime2.append(random.expovariate(lambd=1.0 / self.serviceRate2))

                    # yield an event to the simulator
                    yield self.env.timeout(self.jobTime2[-1])

                    # stores the instant when the job in back server was done
                    self.endTime2.append(self.env.now)

                    self.q2 -= 1
                    # print ("Packets in the Back Server buffer: ", self.q2)

                    # increment the counter to choose the correct time to finish the job
                    self.countJob2 += 1

                    # print ("Service of packet no. %d done in Back Server at: %f" % (self.countJob2, self.env.now))
                self.dropped2vector.append(self.countDropped2)
        else:
            self.pMinusOne += 1
