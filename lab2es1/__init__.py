#!/usr/bin/python
from collections import deque
from numpy import random
import simpy
import device
from device import Device
from shared_folders import SharedFolder
from matplotlib import pyplot
import numpy

SIM_TIME = 100000

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
    NUM_DEV = 50

    # collection of devices
    devices = {}

    # collection of shared folders
    shared_folders = {}

   # u_used_v.append(0)
   # d_used_v.append(0)
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
    x = numpy.linspace(0,len(device.getDUsedV()),len(device.getDUsedV()),endpoint=True)
    down.bar(x,device.getDUsedV())
    down.set_ylabel("D used band")
    x = numpy.linspace(0,len(device.getUUsedV()),len(device.getUUsedV()),endpoint=True)
    up.bar(x,device.getUUsedV())
    up.set_ylabel("UP used band")

    pyplot.show()
