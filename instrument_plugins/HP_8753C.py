# HP_8753C.py class, to perform the communication between the Wrapper and the device
# Pieter de Groot <pieterdegroot@gmail.com>, 2008
# Martijn Schaafsma <mcschaafsma@gmail.com>, 2008
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
from time import sleep
import struct

class HP_8753C(Instrument):
    '''
    This is the python driver for the HP 8753C
    network analyzer

    Usage:
    Initialise with
    <name> = instruments.create('<name>', 'HP_8753C', address='<GPIB address>',
        reset=<bool>)

    The last parameter is optional. Default is reset=False

    TODO:
    1. make todo list
    2. ask Pieter about the purpose of the specific tools
    3. fix docstrings
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the HP_8753C, and communicates with the wrapper

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false
        '''
        Instrument.__init__(self, name)

        self._address = address
        self._visainstrument = visa.instrument(self._address)

        self._visainstrument.timeout = 30
        # BEWARE! in case of low IFWB, it might be
        # necessary to add additional delay
        # ( ~ numpoints / IFBW ) yourself!

        self._visainstrument.send_end = False
        self._visainstrument.term_chars = ''
        # BEWARE! need to end strings with ';' yourself!

        self.add_parameter('IF_Bandwidth', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('numpoints', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('start_freq', flags=Instrument.FLAG_GETSET, type=types.FloatType)
        self.add_parameter('stop_freq', flags=Instrument.FLAG_GETSET, type=types.FloatType)
        self.add_parameter('power', flags=Instrument.FLAG_GETSET, type=types.FloatType)

        self.add_function('set_freq_3GHz')
        self.add_function('set_freq_6GHz')
        self.add_function('set_measurement_S11')
        self.add_function('set_measurement_S22')
        self.add_function('set_measurement_S12')
        self.add_function('set_measurement_S21')
        self.add_function('set_format_logm')
        self.add_function('set_format_phas')
        self.add_function('set_lin_freq')

        self.add_function('set_conversion_off')
        self.add_function('set_average_off')
        self.add_function('set_smooth_off')
        self.add_function('set_correction_off')
        self.add_function('set_trigger_exttoff')

        self.add_function('set_trigger_hold')
        self.add_function('send_trigger')
        self.add_function('reset')

        self.get_all()

    def get_all(self):

        sl = 1

        self.get_start_freq()
        sleep(sl)

        self.get_stop_freq()
        sleep(sl)

        self.get_IF_Bandwidth()
        sleep(sl)

        self.get_numpoints()
        sleep(sl)

        self.get_power()
        sleep(sl)

    def default_init(self):

        sl = 1

        print 'resetting'
        self.reset()
        sleep(sl)

        print 'set trigger hold'
        self.set_trigger_hold()
        sleep(sl)

        print 'set correction off'
        self.set_correction_off()
        sleep(sl)
        print 'set averaging off'
        self.set_average_off()
        sleep(sl)
        print 'set smoothing off'
        self.set_smooth_off()
        sleep(sl)
        print 'set conversion off'
        self.set_conversion_off()
        sleep(sl)
        print 'set trigger exttoff'
        self.set_trigger_exttoff()
        sleep(sl)

        print 'set format logm'
        self.set_format_logm()
        sleep(sl)
        print 'set measurement S21'
        self.set_measurement_S21()
        sleep(sl)

        print 'set start freq'
        self.set_start_freq(10e6)
        sleep(sl)
        print 'set stop freq'
        self.set_stop_freq(3e9)
        sleep(sl)
        print 'set IF bandwidth'
        self.set_IF_Bandwidth(3000)
        sleep(sl)
        print 'set numpoints'
        self.set_numpoints(401)
        sleep(sl)
        print 'set power'
        self.set_power(0.0)
        sleep(sl)

    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('PRES;')

    def set_trigger_hold(self):
        '''
        Puts instrument on hold. It will wait for
        trigger to initiate a trace.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('HOLD;')


    def send_trigger(self):
        '''
        Send trigger to the instrument.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('SING;')

    def read(self):
        '''
        Read the date from the instrument.

        Input:
            None

        Output:
            data (int)  : list of data points
        '''
        data = self._visainstrument.ask('FORM2;DISPDATA;OUTPFORM;')
        d = [struct.unpack('>f', data[i:i+4])[0] for i in range(4, len(data),8)]
        return d

    def set_freq_3GHz(self):
        '''
        Set to 3 GHz range.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('FREQRANG3GHz;')

    def set_freq_6GHz(self):
        '''
        Set to 6 GHz range.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('FREQRANG6GHz;')

    def set_measurement_S11(self):
        '''
        Set S11 measurement.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('S11;')

    def set_measurement_S22(self):
        '''
        Set S22 measurement.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('S22;')

    def set_measurement_S12(self):
        '''
        Set S12 measurement.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('S12;')

    def set_measurement_S21(self):
        '''
        Set S21 measurement.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('S21;')

    def set_lin_freq(self):
        '''
        Set the frequency to linear scale.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('LINFREQ;')

    def set_format_logm(self):
        '''
        Set output format to 'log magnitude'.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('LOGM;')

    def set_format_phas(self):
        '''
        Set output format to 'phase'.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('PHAS;')

### Functions for turning stuff 'off'

    def set_trigger_exttoff(self):
        '''
        Set external trigger input off.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('EXTTOFF;')

    def set_conversion_off(self):
        '''
        Set conversion off.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('CONVOFF;')

    def set_average_off(self):
        '''
        Set averaging off.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('AVEROOFF;')

    def set_smooth_off(self):
        '''
        Set smoothing off.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('SMOOOOFF;')

    def set_correction_off(self):
        '''
        Set correction off.

        Input:
            None

        Output:
            None
        '''
        self._visainstrument.write('CORROFF;CORIOFF;')
 

### parameters

    def _do_set_IF_Bandwidth(self, bw):
        '''
        Set IF Bandwidth.
        Can be 10, 30, 100, 300, 1000, 3000

        Input:
            bw (float)

        Output:
            None
        '''
        self._visainstrument.write('IFBW%d;' %bw)

    def _do_get_IF_Bandwidth(self):
        '''
        Get IF Bandwith.

        Input:
            None

        Output:
            bandwidth (float)   : IF bandwidth
        '''
        return int(float(self._visainstrument.ask('IFBW?;')))

    def _do_set_numpoints(self, numpts):
        '''
        Set number of points in trace.
        Can be 3, 11, 26, 51, 101, 201, 401, 801, 1601

        Input:
            numpts (int)    : number of points in trace

        Output:
            None
        '''
        self._visainstrument.write('POIN%d;' %numpts)

    def _do_get_numpoints(self):
        '''
        Get number of points in trace

        Input:
            None

        Output:
            numpoints (int) : Number of points in trace
        '''
        return int(float(self._visainstrument.ask('POIN?;')))

    def _do_set_start_freq(self, freq):
        '''
        Set start frequency.

        Input:
            freq (float)    : Start frequency

        Output:
            None
        '''
        self._visainstrument.write('STAR%eHZ;' %freq)

    def _do_get_start_freq(self):
        '''
        Get start frequency.

        Input:
            None

        Output:
            freq (float)    : Start frequency
        '''
        return float(self._visainstrument.ask('STAR?;'))

    def _do_set_stop_freq(self, freq):
        '''
        Set stop frequency.

        Input:
            freq (float)    : Stop frequency

        Output:
            None
        '''
        self._visainstrument.write('STOP%eHZ;' %freq)

    def _do_get_stop_freq(self):
        '''
        Get stop frequency.

        Input:
            None

        Output:
            freq (float)    : Stop frequency
        '''
        return float(self._visainstrument.ask('STOP?;'))

    def _do_set_power(self, pow):
        '''
        Set power.

        Input:
            pow (float) : Power

        Output:
            None
        '''
        self._visainstrument.write('POWE%.3e;' % pow)

    def _do_get_power(self):
        '''
        Get power

        Input:
            None

        Output:
            pow (float) : Power
        '''
        return float(self._visainstrument.ask('POWE?;'))

