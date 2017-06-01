#!/usr/bin/python
from collections import deque
from numpy import random
import simpy
import time
import Queue
from matplotlib import pyplot
import numpy




D_BAND = 20e6
U_BAND = 5e6
SIZE = 10e6
clients = 0
u_band_occ = 0
d_band_occ = 0
u_used_v = []
d_used_v = []
SIM_TIME = 5000

def getDUsedV():
    return d_used_v

def getUUsedV():
    return u_used_v

class Device():
    # cosftructor
    def __init__(self, id, env=None):
        self.id = id
        self.my_shared_folders = []
        self.my_upload_band_v = []
        self.my_download_band_v = []
        self.tp_size = []
        self.my_u_used = 0
        self.my_d_used = 0
        self.q = Queue.Queue()
        self.env = env
        self.coda = True

    # fancy printing as string
    def __str__(self):
        sf_str = ", ".join([str(i) for i in self.my_shared_folders])
        return "Device: " + str(self.id) + ", Shared Folders [" + sf_str + "]"

    def setEnv(self,env):
        self.env = env


    def getIdFolder(self):
        x = []
        for f in self.my_shared_folders:
            x.append(f.getId())
        return x

    def getFolderFromId(self,id):
        for fold in self.my_shared_folders:
            if str(fold.getId()) == str(id):
                return fold


    def pushQueue(self,item):
        self.q.put(item)

    def getId(self):
        return self.id

    # add a shared folder to this device
    def add_shared_folder(self, sf):
        self.my_shared_folders.append(sf)

    def readFromFile(self,file):
        list =  []
        x = open(file, 'r')
        for line in x:
            line_split = line.split()
            dict = {'size': float(line_split[0]),
                    'tp': float(line_split[1])/8}
            list.append(dict)
        return list



    def deviceP(self):
        global clients

        self.tp_size = self.readFromFile('throughput.txt')

        while True:
            clients += 1
            yield self.env.process(self.imOnline(1))
            clients-=1
            yield self.env.process(self.imOffline())


    def imOffline(self):

        inter_arrival = random.lognormal(mean=7.971,sigma=1.308)
        yield self.env.timeout(inter_arrival)


    def imOnline(self,timeout):
        # sample the time to next arrival
        inter_arrival = random.lognormal(mean=8.492,sigma=1.545)
        # when a user goes online, randomly selects a folder to which upload and evaluate the end time of its online session
        try:
            final = self.env.now + inter_arrival
            randF = random.choice(self.getIdFolder())

            while self.env.now < final:
                inter_upload = random.lognormal(mean = 3.748, sigma=2.286)
                yield self.env.process(self.inDownload(final))
                yield self.env.timeout(inter_upload)
                yield self.env.process(self.imUploading(final,randF))
            #print('Finito online',env.now)

        except Exception as e:
            print (e.message)


    def imUploading(self,final,randF):

            global u_band_occ
            global u_used_v

            #print ('randf', randF,self.id)
            fold = self.getFolderFromId(randF)
            devices = fold.getDevices()

            row = numpy.random.randint(0, len(self.tp_size)-1)

            stringa = str(self.id) + " in folder " + str(fold.getId())
            file = {'file': stringa,
                    'size': self.tp_size[row]['size'],
                    'tp':self.tp_size[row]['tp']}

            for d in devices:
                if d.getId() != self.id:

                    try:

                        if (final - self.env.now > file['size']/file['tp']):
                            u_band_occ = u_band_occ + file['tp']
                            u_used_v.append(u_band_occ)
                            #print ('STO UPLOAD',self.id,u_band_occ)

                            #print (file,env.now)
                            d.pushQueue(file)
                            yield self.env.timeout(file['size']/file['tp'])
                            u_band_occ = u_band_occ - file['tp']
                            u_used_v.append(u_band_occ)

                    except Exception as e:
                        print (e.message)



    def inDownload(self,final):

        # the device pulls packets from the queue and downloads them till the queue is empty
        global d_band_occ
        global d_used_v

        while not self.q.empty():
            x = self.q.get()
            try:
                if (final-self.env.now>x['size']/x['tp']):
                    d_band_occ = d_band_occ + x['tp']
                    d_used_v.append(d_band_occ)

                    yield self.env.timeout(x['size']/x['tp'])
                    d_band_occ = d_band_occ - x['tp']
                    d_used_v.append(d_band_occ)
            except Exception as e:
                print (e.message)