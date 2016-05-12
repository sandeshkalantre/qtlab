# a34410a.py driver for Agilent 2000 DMM
# IST Austria 2016
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import visa
import types
import logging
import numpy



class a34410a(Instrument):
    """ A34410a: Agilent 34410A Multimeter """
    def __init__(self,name=None,address=None):
        
        # Initialize wrapper functions
        logging.info('Initializing instrument Keithley_2000')
        Instrument.__init__(self, name, tags=['physical'])
        
        # Add some global constants
        self._name = name
        self._address = address
        if self._address != None:
            self._visainstrument = visa.instrument.open_resource(self._address)
        else:    
            self._visainstrument = None
            
            
        # Add parameters to wrapper
        self.add_parameter('readval', flags=Instrument.FLAG_GET,
            units='AU',
            type=types.FloatType,
            tags=['measure']) 
            
        self.add_parameter('setup', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=0.01, maxval=50) 
            
        self.add_parameter('NPLC',
            flags=Instrument.FLAG_GETSET,
            units='#', type=types.FloatType, minval=0.01, maxval=50)     
            
            

    def _write(self,com):
        self._visainstrument.write(com)

    def _query(self,com):
        return self._visainstrument.query(com)

    def SCPI(self, command):
        if command[-1]!='?':
            self._write(command)
        else:
            return self._query(command)
            
    #def get(self):
       # return float(self._query("MEAS:VOLT:DC?"))
        
    def do_get_readval(self):
        return float(self._query("READ?"))
    
    #def get(self):   # Same function as do_get_readval - to be compatible with previous convention
        #return float(self._query("READ?"))
        
    def do_set_setup(self, nplc = 0.2):
        self._write("CONF:VOLT:DC")
        self._write("VOLT:DC:NPLC " + str(nplc))

    def do_set_NPLC(self,nplc=1.0):
        self._write("VOLT:DC:NPLC " + str(nplc))
        
    def do_get_NPLC(self):
        return self._query("VOLT:DC:NPLC?")
    
    def Config(self,F='VDC'):
        func_dict={'VDC': 'CONF:VOLT:DC', 'VAC': 'CONF:VOLT:AC'}
        return self._write(func_dict[F])
        
    def Reading(self, R='Mod'):
        '''
        SLOW: NPLC = MAX (100)
        MOD:  NPLC = 1
        FAST: NPLC = MIN (0.006)
        '''
        conf = self._query('CONF?')
        print conf
        read_dict={'SLOW':'VOLT:DC:NPLC', 'MOD':'VOLT:DC:NPLC 1'}
   
   
        
        
        
        