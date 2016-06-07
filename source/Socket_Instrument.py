#-------------------------------------------------------------------------------
#  Get a screen catpure from DPO4000 series scope and save it to a file

# python        2.7         (http://www.python.org/)
# numpy         1.6.2       (http://numpy.scipy.org/)
# MatPlotLib    1.0.1       (http://matplotlib.sourceforge.net/)
#-------------------------------------------------------------------------------

import socket
import numpy as np
from struct import unpack
import pylab
import time
import select


class Socket_Instrument(object):
    ''' socket replacement for visa.instrument class'''
    def __init__(self, IPaddress, PortNumber = 4000, timeout = 10):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((IPaddress, PortNumber))
        self.s.setblocking(0)
        self.s.settimeout(timeout)

    def write(self, cmd):
        self.s.send(cmd + '\n')

    def ask(self, cmd, buffer = 1024, timeout = 5):

        self.clear()
        self.write(cmd + "\n")
        return self.read()
        #self.s.send(cmd + '\n')
        #response = ''   
        #while True:

            #char = ""
            #try:
            #    char = self.s.recv(24)
            #    if char == '':
            #        break
            #except:
            #    time.sleep(0.1)
            #    if response.rstrip() != "":
            #        break
            #if char:
            #    response += char

        #return response.rstrip()

    def read(self):
        response = ''
        while True:
            char = ""
            try:
                char = self.s.recv(1)
            except:
                time.sleep(0.1)
                if response.rstrip() != "":
                    break
            if char:
                response += char
        return response.rstrip()

    def close(self):
        self.s.close()

    def clear(self):
        rlist, wlist, xlist = select.select([self.s], [], [], 0)
        if len(rlist) == 0:
            return
        ret = self.read()