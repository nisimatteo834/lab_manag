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
SIZE = 20e6
clients = 0
u_band_occ = 0
d_band_occ = 0
u_used_v = []
d_used_v = []
SIM_TIME = 5000

#******************************************************************************
# class representing the shared folders
#******************************************************************************
class SharedFolder(object):
    # cosftructor
    def __init__(self, id):
        self.id = id
        self.my_devices = []
        self.content = {}

    # fancy printing as string
    def __str__(self):
        return str(self.id)

    def getId(self):
        return self.id

    def insertContent(self,file,iduser):
        self.content['file'] = file
        self.content['user'] = iduser
        #print (self.content,self.id,time.time())
        return

    def getContent(self):
        return self.content

    def getLen(self):
        return len(self.content)

    def getDevices(self):
        return self.my_devices

    def getStDevices(self):
        lista = []
        for x in self.my_devices:
            lista.append(x.getId())
        return lista

    # add a device to the list of devices registering this shared folder
    def add_device(self, device):
        self.my_devices.append(device)



#******************************************************************************
# class representing devices
#******************************************************************************
class Device():
    # cosftructor
    def __init__(self, id, env=None):
        self.id = id
        self.my_shared_folders = []
        self.my_upload_band_v = []
        self.my_download_band_v = []
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


    def deviceP(self):
        global clients
        while True:
            clients += 1
            #print(clients, ' users online')
            yield self.env.process(self.imOnline(1))
            clients-=1
            #print(clients,' users online')
            yield self.env.process(self.imOffline())


    def imOffline(self):

        inter_arrival = random.lognormal(mean=7.971,sigma=1.308)
        #print (self.id,'Offline!',env.now)
        yield self.env.timeout(inter_arrival)
        #print ('Offline finito!',env.now)


    def imOnline(self,timeout):
        # sample the time to next arrival
        inter_arrival = random.lognormal(mean=8.492,sigma=1.545)

        try:
            final = env.now + inter_arrival
            randF = random.choice(self.getIdFolder())

            while env.now < final:
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

            stringa = str(self.id) + " in folder " + str(fold.getId())
            file = {'file': stringa,
                    'size': SIZE}

            for d in devices:
                if d.getId() != self.id:
                    # stringa = str(self.id) +" a "+ str(d.getId()) + " in folder " + str(fold.getId())
                    # file = {'file': stringa,
                    #         'size': SIZE}

                    if (final - env.now > file['size']/U_BAND):
                        # self.my_u_used = self.my_u_used + U_BAND
                        # self.my_upload_band_v.append(self.my_u_used)
                        u_band_occ = u_band_occ + U_BAND
                        u_used_v.append(u_band_occ)
                        #print ('STO UPLOAD',self.id,u_band_occ)

                        #print (file,env.now)
                        d.pushQueue(file)
                        yield env.timeout(file['size']/U_BAND)
                        u_band_occ = u_band_occ - U_BAND
                        u_used_v.append(u_band_occ)
                        #print('Upload finito', env.now,self.id,str(d.getId()))
                        #print ('UPLOAD FIN',self.id,u_band_occ)


    def inDownload(self,final):

        # if self.q.empty():
        #     yield env.timeout(1)
        # else:
        #
        global d_band_occ
        global d_used_v
        while not self.q.empty():
            x = self.q.get()
            if (final-env.now>x['size']/D_BAND):
                d_band_occ = d_band_occ + D_BAND
                d_used_v.append(d_band_occ)
                #print (x,self.id,env.now)
                #print ('STO SCARICANDO QUALCOSA',env.now,self.id)
                yield env.timeout(x['size']/D_BAND)
                d_band_occ = d_band_occ - D_BAND
                d_used_v.append(d_band_occ)
            #self.coda = False
        #print ('Ho SCARICATO tutto',env.now,self.id)

#******************************************************************************
# Create the synthetic content synchronization network
#******************************************************************************
def generate_network(num_dv, devices, shared_folders):

    # shared folders per device - negative_binomial (s, mu)
    DV_DG = [0.470, 1.119]

    # device per shared folder - negative_binomial (s, mu)
    SF_DG = [0.231, 0.537]

    # derive the expected number of shared folders using the negative_binomials


    # this piece is just converting the parameterization of the
    # negative_binomials from (s, mu) to "p". Then, we use the rate between
    # the means to estimate the expected number of shared folders
    # from the given number of devices

    dv_s = DV_DG[0]
    dv_m = DV_DG[1]
    dv_p = dv_s / (dv_s + dv_m)
    nd = 1 + (dv_s * (1.0 - dv_p) / dv_p)

    sf_s = SF_DG[0]
    sf_m = SF_DG[1]
    sf_p = sf_s / (sf_s + sf_m)
    dn = 1 + (sf_s * (1.0 - sf_p) / sf_p)

    # the number of shared folders is finally derived
    num_sf = int(num_dv * nd / dn)

    # sample the number of devices per shared folder (shared folder degree)
    sf_dgr = [x + 1 for x in random.negative_binomial(sf_s, sf_p, num_sf)]

    # sample the number of shared folders per device (device degree)
    dv_dgr = [x + 1 for x in random.negative_binomial(dv_s, dv_p, num_dv)]

    # create the population of edges leaving shared folders
    l = [i for i, j in enumerate(sf_dgr) for k in range(min(j, num_dv))]
    random.shuffle(l)
    sf_pop = deque(l)

    # create empty shared folders
    for sf_id in range(num_sf):
        shared_folders[sf_id] = SharedFolder(sf_id)

    # first we pick a random shared folder for each device
    for dv_id in range(num_dv):
        devices[dv_id] = Device(dv_id)

        sf_id = sf_pop.pop()
        devices[dv_id].add_shared_folder(shared_folders[sf_id])
        shared_folders[sf_id].add_device(devices[dv_id])

    # then we complement the shared folder degree

    # we skip devices with degree 1 in a first pass, since they just got 1 sf
    r = 1

    # we might have less edges leaving devices than necessary
    while sf_pop:
        # create the population of edges leaving devices
        l = [i for i, j in enumerate(dv_dgr) for k in range(min(j - r, num_sf))]
        random.shuffle(l)
        dv_pop = deque(l)

        # if we need to recreate the population, we use devices w/ degree 1 too
        r = 0

        while sf_pop and dv_pop:
            dv = dv_pop.pop()
            sf = sf_pop.pop()

            # we are lazy and simply skip the unfortunate repetitions
            if not shared_folders[sf] in devices[dv].my_shared_folders:
                devices[dv].add_shared_folder(shared_folders[sf])
                shared_folders[sf].add_device(devices[dv])
            else:
                sf_pop.append(sf)


#******************************************************************************
# implements the simulation
#******************************************************************************
if __name__ == '__main__':
    #global u_used_v
    #global d_used_v
    # number of devices in the simulation
    NUM_DEV = 10

    # collection of devices
    devices = {}

    # collection of shared folders
    shared_folders = {}

    u_used_v.append(0)
    d_used_v.append(0)
    # create the content sharing network
    env = simpy.Environment()
    generate_network(NUM_DEV, devices, shared_folders)


    #for fold in shared_folders:
        #print (fold,shared_folders[fold].getStDevices())

    # DEBUG: dumping the network
    for dev_id in devices:
        #print (str(devices[dev_id]))
        devices[dev_id].setEnv(env)
        env.process(devices[dev_id].deviceP())

    env.run(until=SIM_TIME)

    fig,(down,up) = pyplot.subplots(2,1)
    x = numpy.linspace(0,len(d_used_v),len(d_used_v),endpoint=True)
    down.bar(x,d_used_v)
    x = numpy.linspace(0,len(u_used_v),len(u_used_v),endpoint=True)
    up.bar(x,u_used_v)

    pyplot.show()


