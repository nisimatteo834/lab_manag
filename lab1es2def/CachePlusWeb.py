
import simpy
import numpy
from decimal import Decimal
from matplotlib import pyplot
import random
import Queue

class cachePlusWeb(object):

    # constructor
    def __init__(self, env, bs1, nm1, st1, bs2, nm2, st2, tsh):

        self.qFront = 0
        self.qBack = 0


        # probability threshold for a packet to go to the back server
        self.tsh = tsh

        # buffer size of web cache
        self.bs1 = bs1

        # service time of web cache
        self.st1 = st1
        self.service_time1 = 0

        # number of machines
        self.nm1 = nm1

        #buffer size of web server
        self.bs2 = bs2

        #number of web servers
        self.nm2 = nm2

        #service time of web server
        self.st2 = st2
        self.service_time2 = 0


        #
        self.machines1 = simpy.Resource(env, nm1)
        self.machines2 = simpy.Resource(env,nm2)

        # the environment
        self.env = env

        # number of cars in the shop
        self.q_memory = []

        #Queues are used to process the packets in order, as a real buffer
        self.queue1 = 0
        self.queue2 = 0

        # to keep trace of the response time, of front server, back server and total system
        self.response_time1 = []
        self.response_time2 = []
        self.total_response_time = []

        # to keep trace of the buffer occupancy
        self.bo1 = []
        self.bo2 = []


        #Counter for the dropped packets
        self.numberPacketDroppedFront = 0
        self.numberPacketDroppedBack = 0

    # Web Cache
    def frontEnd(self,packetreceived):
        self.qFront +=1
        enter = self.env.now
        if self.qFront > self.bs1:
            print ('Packet',packetreceived,'dropped')
            self.numberPacketDroppedFront += 1
            self.qFront -=1
            self.bo1.append(self.qFront)

        else:
            with self.machines1.request() as request1:
                self.bo1.append(self.qFront)
                print ('Packet',packetreceived,'in Q1 asks for',request1,self.env.now)
                yield request1
                print ('Packet',packetreceived,'obtains',request1,self.env.now)
                yield self.env.timeout(random.expovariate(lambd=1.0/self.st1))
                print ('Packet',packetreceived,'releases in Q1',request1,self.env.now)
            self.qFront -= 1
            self.response_time1.append(self.env.now - enter)
            self.bo1.append(self.qFront)



            p = numpy.random.uniform(0, 1)

            if p <= self.tsh:
                self.qBack +=1
                if self.qBack > self.bs2:
                    print (packetreceived,'dropped in Q2')
                    self.numberPacketDroppedBack +=1
                    self.qBack -=1
                    self.bo2.append(self.qBack)
                else:
                    print (packetreceived, 'enters Q2 at', self.env.now)
                    self.bo2.append(self.qBack)
                    enter2 = self.env.now
                    with self.machines2.request() as request2:
                        print (packetreceived, 'in Q2 is asking for', request2)
                        yield request2
                        print(packetreceived, 'in Q2 has obtained', request2,self.env.now)
                        service = random.expovariate(lambd=1.0 / self.st2)
                        print (service)
                        yield self.env.timeout(service)
                        print (packetreceived, 'in Q2 releases', request2,self.env.now)
                    self.qBack -= 1
                    self.bo2.append(self.qBack)
                    self.response_time2.append(self.env.now - enter2)

            else:
                self.response_time2.append(0)

            self.total_response_time.append(self.env.now-enter)
