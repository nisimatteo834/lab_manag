from collections import deque
from numpy import random
import numpy
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
band_s_occupancy = []
users_online = {}

def getOccupancy():
    return band_s_occupancy;

class Device():
    # cosftructor
    def __init__(self, id, env=None):
        self.id = id
        self.final = 0
        self.my_shared_folders = []
        self.downloaded_files = []
        self.active_peers = []
        self.d_peer = {}
        self.d_server = {}
        self.q = Queue.Queue()
        self.env = env
        self.coda = True

        #toDo differenziare file da p2p da quelli server in rapporto al numero di peer da cui scarica

    # fancy printing as string
    def __str__(self):
        sf_str = ", ".join([str(i) for i in self.my_shared_folders])
        return "Device: " + str(self.id) + ", Shared Folders [" + sf_str + "]"

    def setEnv(self,env):
        self.env = env

    def setFinal(self,final):
        self.final = final

    def getFinal(self):
        return self.final

    def getDPeer(self):
        return self.d_peer

    def getDServer(self):
        return self.d_server

    def getDownloadedFiles(self):
        return self.downloaded_files

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
            print(clients, ' users are currently online')
            yield self.env.process(self.imOnline(1))
            clients-=1
            print(clients,' users are currently online')
            yield self.env.process(self.imOffline())


    def imOffline(self):
        global users_online
        inter_arrival = random.lognormal(mean=7.971,sigma=1.308)
        print (self.id,'Offline!',self.env.now)
        yield self.env.timeout(inter_arrival)
        print ('Offline finito!',self.env.now)


    def imOnline(self,timeout):
        # sample the time to next arrival
        inter_arrival = random.lognormal(mean=8.492,sigma=1.545)

        global users_online

        try:
            final = self.env.now + inter_arrival
            self.setFinal(final)
            randF = random.choice(self.getIdFolder())
            users_online[self.getId()]= final

            while self.env.now < self.final:
                inter_upload = random.lognormal(mean = 3.748, sigma=2.286)
                yield self.env.process(self.inDownload(final))
                yield self.env.timeout(inter_upload)
                yield self.env.process(self.imUploading(final,randF))
            print('Finito online',self.env.now)

        except Exception as e:
            print (e.message)


    def imUploading(self,final,randF):

            global u_band_occ
            #print ('randf', randF,self.id)
            fold = self.getFolderFromId(randF)
            devices = fold.getDevices()

            stringa = str(self.id) + " in folder " + str(fold.getId()) + " " + str(self.env.now)
            file = {'file': stringa,
                    'folder': str(fold.getId()),
                    'size': SIZE}

            if (final - self.env.now > file['size'] / U_BAND):
                u_band_occ = u_band_occ + U_BAND
                #print (file, self.env.now)
                yield self.env.timeout(file['size'] / U_BAND)
                self.downloaded_files.append(file)

                for d in devices:
                    if d.getId() != self.id:
                            d.pushQueue(file)
                            u_band_occ = u_band_occ - U_BAND
                            #print('Upload finito', self.env.now, self.id, str(d.getId()))



    def inDownload(self,final):

        # if self.q.empty():
        #     yield self.env.timeout(1)
        # else:
        #
        global d_band_occ
        global d_band_server
        while not self.q.empty():
            server = False
            x = self.q.get()
            enter = self.env.now
            if (final-self.env.now>x['size']/D_BAND):
                folder_id = x['folder']
                folder = self.getFolderFromId(folder_id)


                if len(folder.getStDevices()) > 1 :
                    downloaded_chunck = 0
                    chuncks = {}
                    print ('Je suis', str(self.getId()),self.env.now)  # todo ERASE

                    while downloaded_chunck != int(x['size']/MAX_CHUNCK) and not server:

                        #todo dizionario di dizionari per avere una statistica di tempo per ogni chunk legata
                        #al numero di peer che ci stanno servendo
                        #grafico x = tempo y = chunk scaricati
                        print ('File',x['file'],'shared with',folder.getStDevices())
                        count = 0
                        for device in folder.getDevices():
                            if (users_online[device.getId()] > self.env.now + MAX_CHUNCK / U_BAND) and (x in device.getDownloadedFiles()) :
                                count = count + 1
                                print ('count:',count)
                                print (str(device.getId()), 'has this files',x['file'])#, device.getDownloadedFiles())
                                if not chuncks.has_key(downloaded_chunck):
                                    chuncks[downloaded_chunck] = device.getId()
                                    print (str(self.getId()),'is downloading file',x['file'],'chunck',downloaded_chunck,'from',device.getId(),'at',self.env.now)
                                    downloaded_chunck = downloaded_chunck + 1 #TODO forse ne abbiamo uno in piu
                                    if downloaded_chunck == int(x['size']/MAX_CHUNCK):
                                        break
                        self.active_peers.append(count)
                        if count == 0: #se non ci sono device disponibili al download vado nel server
                            server = True
                            d_band_server = d_band_server + D_BAND
                            band_s_occupancy.append(d_band_server)
                            remaining_data = (x['size'] - MAX_CHUNCK*downloaded_chunck)
                            if (final - self.env.now > remaining_data/ D_BAND):
                                print (self.getId(), 'is downloading from the server cause count 0', folder.getStDevices())
                                start = self.env.now
                                #il server va a scaricare solo la rimanente parte del file
                                #naturalmente se siamo al chunck 0 scarica tutto
                                yield self.env.timeout(float(remaining_data)/ D_BAND)
                                self.downloaded_files.append(x)
                                self.d_server[x['file']] = {'exit': self.env.now,
                                                            'enter': start,
                                                            'time': self.env.now - enter
                                                            }
                                print ('Ho scaricato tutto dal server', self.env.now, self.id)
                                d_band_server = d_band_server - D_BAND
                                band_s_occupancy.append(d_band_server)
                                break

                        else:
                            yield self.env.timeout(MAX_CHUNCK/U_BAND)
                            band_s_occupancy.append(d_band_server)

                    if not server:
                        #todo tenere traccia di quanti chunck ho scaricato
                        #if #todo capire questo if per cosa l'avevi messo
                        self.d_peer[x['file']] = {'exit' : self.env.now,
                                                  'enter': enter,
                                                  'time': self.env.now - enter,
                                                  'avg_peers': numpy.mean(self.active_peers)
                                                  }
                    print ('HO FINITO DI PRENDERE TUTTI I CHUNK',str(self.getId()),x['file'],self.env.now)
                    print (self.getDownloadedFiles())

                    self.downloaded_files.append(x)

                else:
                    d_band_server = d_band_server + D_BAND
                    band_s_occupancy.append(d_band_server)

                    if (final - self.env.now > x['size']/D_BAND):
                        print (self.getId(),'is downloading from the server',folder.getStDevices())
                        self.downloaded_files.append(x)
                        start = self.env.now
                        yield self.env.timeout(x['size']/D_BAND)
                        print ('Ho scaricato tutto dal server',self.env.now,self.id)
                        self.d_server[x['file']] = {'exit' : self.env.now,
                                                    'enter': start,
                                                    'time': self.env.now - enter
                                                  }
                    d_band_server = d_band_server - D_BAND
                    band_s_occupancy.append(d_band_server)
