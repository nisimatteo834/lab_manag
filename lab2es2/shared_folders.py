from collections import deque
from numpy import random
import simpy
import time
import Queue

D_BAND = 20e6
U_BAND = 5e6
SIZE = 10e6
MAX_CHUNCK = 1e6
clients = 0
u_band_occ = 0
d_band_occ = 0
d_band_server = 0
users_online = {}


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
        print (self.content,self.id,time.time())
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
