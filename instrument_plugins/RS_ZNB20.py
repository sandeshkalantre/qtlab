# RS_ZNB20 class, to perform the communication between the Wrapper and the device
# Sandesh Kalantre <kalantresandesh@gmail.com>
# Josip Kukucka <josip.kukucka@ist.ac.at>
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

import pyvisa
import logging
import time
import types
from instrument import Instrument
import matplotlib.pyplot as plt

import pyvisa.constants as pvc

class RS_ZNB20(Instrument):
    ''' ZNB20: Vector network analyzer from Rohde&Schwarz '''
    def __init__(self, name, address, init_dict_update=None):

        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])
        
        # In init_dict there are predefined values for VNA initialization
        self.init_dict = {'Address': address,
                     'Meas_param':'S21',
                     'Cont_off/on':'OFF',
                     'Num_of_sweep_points' : 200,  
                     'Num_of_sweeps' : 1, 
                     'Averaging' : 'OFF', 
                     'BW' : 10, 
                     'Source_power' : -30, 
                     'Data_format' : 'MLIN', 
                     'VNA_mode' : 'MLOG',
                     'Start_freq': 50,
                     'Stop_freq': 100,
                     'Center_freq' : 200 
                    }
                    
        if init_dict_update is not None:      # Updating of predefined values with user selected values from init_dict_update
            self.init_dict.update(init_dict_update)
                    
        if self.init_dict['Num_of_sweeps'] > 1:  # If more sweeps are choosen then they should be averaged
            self.init_dict['Averaging'] = 'ON'
            
        
        # In command_dict there are non formatted string of commands for VNA initialization
        # Complete commands are assembled by string formatting command_dict dictionary with init_dict
        
        self.command_dict = {'A_Rst' : '*RST',
                        'B_Cont_off/on' :' INIT1:CONT {Cont_off/on} ',                         # Countinuous mode ON/OFF
                        
                        'C_Auto_swp_time' : 'SENS1:SWE:TIME:AUTO ON; TRIG1:SEQ:SOUR IMM',      # Avoid a delay time between different partial measurements and before the 
                                                                                               # Start of the sweeps and minimize sweep time (is default setting)
                                                                                     
                        'D_Num_of_sweep_points' : 'SENS1:SWE:POIN {Num_of_sweep_points}',      # Number of sweep points
                        'E_Num_of_sweeps' : 'SENS1:SWE:COUNT {Num_of_sweeps}',
                        'F_Averaging' : 'SENS1:AVER:COUN {Num_of_sweeps};  :AVER {Averaging}; CLE', # Number of consecutive sweeps to be combined for the sweep average, average ON /OFF, clearing average
                        #'Adj_Averaging':'CALC:SMO ON; :APER 0.5',                             # There is also an option Smoothing - averaging between adjacent sweep points in percentage of overall num of points
                        'G_BW' : 'SENS1:BAND:RES {BW} kHz',                                    # Bandwidth selection in kHz - select the widest bandwidth compatible with your measurement
                        'H_Meas_param' : 'CALCULATE1:PARAMETER:SDEFINE "Trc1", {Meas_param}',  # Measured parameter choosing
                        'I_Display_param' : "DISPLAY:WINDOW1:TRACE5:FEED 'Trc1'",              # Show choosen parameter on display
                        'J_Set_param_active' : "CALCULATE1:PARAMETER:SELECT 'Trc1'",           # Choosen parameter set to active
                        'K_Source_power' : 'SOUR:POW {Source_power}',                          # Setting source power in dBm (available from -30dBm to 10dBm)
                        'L_Data_format' : 'CALC:FORM {Data_format}',                           # Setting up data format on y axes (MLIN - linear mag, MLOG - magnitude in dB, PHAS - Phase in deg, UPH - unwrapped phase in deg)
                        'M_VNA_mode' : 'SENS:SWE:TYPE {VNA_mode}',                             # Choosing VNA mode (MLOG - Linear frequency sweep at constant source power, POIN - CW mode sweep )
                        'N_Start_stop_freq' : 'FREQ:STAR {Start_freq} MHz; STOP {Stop_freq} MHz',      #Setting stop and start frequency for frequency sweep measurement (Active only in MLOG mode)
                        'O_Center_freq' : 'SOUR:FREQ:FIX {Center_freq} MHz',                           #Setting source frequency for time measurement (Active only in POIN mode)
                        }
         
                                       
        if self.init_dict['VNA_mode'] == 'POIN':     # Deleting of unnecessary command depending of the choosen VNA mode
            del self.command_dict['N_Start_stop_freq']
        else:
            del self.command_dict['O_Center_freq']
            
        
        self._address = self.init_dict['Address']
        self._visainstruments = pyvisa.ResourceManager()
                          

        if self._address is not None:        # Opening VISA session for the VNA
            self._visainstrument = self._visainstruments.open_resource(self._address)
        else:
            self._visainstrument = None
            
        del self._visainstrument.timeout     # Timeout deleting - infinite waiting time for instrument response   
    
        self.lib = self._visainstrument.visalib
                
        self._clear()    # Clear buffer
        
        for key in sorted(self.command_dict.keys()):               # Writing initialization commands to VNA
            self._write(self.command_dict[key].format(**self.init_dict))

        self.add_function('reset')
        self.add_function('set_param_active')
        self.add_function('set_display_param')
        self.add_function('set_averaging_on')
        self.add_function('set_averaging_off')
        self.add_function('get_point')
        self.add_function('get_trace')



        self.add_parameter('cont_mode_ON_OFF', type=types.StringType,
            flags=Instrument.FLAG_GETSET| Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('output_state_ON_OFF', type=types.StringType,
            flags=Instrument.FLAG_GETSET| Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('num_of_sweep_points', type=types.IntType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('num_of_sweeps', type=types.IntType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('averaging_count', type=types.IntType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('start_freq', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('stop_freq', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('CW_freq', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('bw', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('source_power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('vna_mode', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('data_format', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('meas_param', type=types.StringType,
            flags=Instrument.FLAG_SET | Instrument.FLAG_GET_AFTER_SET)
         
     # Functions
    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Resetting instrument')
        self._visainstrument.write('*RST')     
    def do_get_cont_mode_ON_OFF(self):
        '''
            Get the status of continuous mode

            Input:
                None
            Output:
                cont_mode (string): 'on'/'off'
        '''
        logging.debug(__name__ + ' : reading continous mode from instrument')
        stat = str(int(self._visainstrument.ask('INIT1:CONT?')))

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Continous mode not specified : %s' % stat) 

    def do_set_cont_mode_ON_OFF(self,cont_mode):
        '''
            Sets continous mode ON/OFF

            Input:
                cont_mode (string) : 'on'/'off'

            Output:
                None
        '''
        logging.debug(__name__ + ' : setting continous mode to "%s"' % cont_mode)
        if cont_mode.upper() in ('ON', 'OFF'):
            cont_mode = cont_mode.upper()
        else:
            raise ValueError('set_cont_mode(): can only set on or off')
        self._visainstrument.write('INIT1:CONT %s' % cont_mode)
    
    #def do_get_cont_mode(self):
     #   '''
     #       Get the status of continuous mode#

            #Input:
            #    None
            #Output:
            #    cont_mode (string): 'on'/'off'
        #'''
        #logging.debug(__name__ + ' : reading continous mode from instrument')
        #stat = str(int(self._visainstrument.ask('INIT1:CONT?')))

        
        #if stat == '1':
        #     return 'on'
        #elif stat == '0':
        #    return 'off'
        #else:
        #    raise ValueError('Continous mode not specified : %s' % stat)  

    def do_get_output_state_ON_OFF(self):
        '''
            Get the status of output status on all ports - ON/OFF

            Input:
                None
            Output:
                output_state (string): 'on'/'off'
        '''
        logging.debug(__name__ + ' : reading output state from instrument')
        stat = str(int(self._visainstrument.ask('OUTP?')))

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Continous mode not specified : %s' % stat)

    def do_set_output_state_ON_OFF(self,output_state):
        '''
            Sets the status of output status on all ports - ON/OFF

            Input:
                output_state (string) : 'on'/'off'

            Output:
                None
        '''
        logging.debug(__name__ + ' : setting output state to "%s"' % output_state)
        if output_state.upper() in ('ON', 'OFF'):
            output_state = output_state.upper()
        else:
            raise ValueError('set_output_state_ON_OFF(): can only set on or off')
        self._visainstrument.write('OUTP %s' % output_state)




    def do_get_num_of_sweeps(self):
        '''
        # Number of sweeps
        '''
        val = str(int(self._visainstrument.ask('SENS1:SWE:COUNT?')))
        return val
    def do_set_num_of_sweeps(self,Num_of_sweeps, ):
        '''
        # Number of sweeps
        '''
        self._visainstrument.write('SENS1:SWE:COUNT {Num_of_sweeps}'.format(Num_of_sweeps=Num_of_sweeps,))

    def do_get_num_of_sweep_points(self):
        '''
        # Number of sweep points
        '''
        val = str(int(self._visainstrument.ask('SENS1:SWE:POIN?')))
        return val
    def do_set_num_of_sweep_points(self,Num_of_sweep_points, ):
        '''
        # Number of sweep points
        '''
        self._visainstrument.write('SENS1:SWE:POIN {Num_of_sweep_points}'.format(Num_of_sweep_points=Num_of_sweep_points,))

    
    def do_get_CW_freq(self):
        '''
        #Getting source frequency for time measurement (Active only in POIN mode)
        '''
        val = str(float(self._visainstrument.ask('SOUR:FREQ:FIX?')))
        return val
    def do_set_CW_freq(self,center_freq, ):
        '''
        #Setting source frequency for time measurement (Active only in POIN mode)
        '''
        self._visainstrument.write('SOUR:FREQ:FIX {center_freq}'.format(center_freq=center_freq,))
    
    def do_get_start_freq(self):
        '''
        #Getting start frequency for frequency sweep measurement (Active only in MLOG mode)
        '''
        val = str(float(self._visainstrument.ask('FREQ:STAR?')))
        return val
    def do_set_start_freq(self,start_freq, ):
        '''
        #Setting start frequency for frequency sweep measurement (Active only in MLOG mode)
        '''
        self._visainstrument.write('FREQ:STAR {start_freq}'.format(start_freq=start_freq,))

    def do_get_stop_freq(self):
        '''
        #Getting stop frequency for frequency sweep measurement (Active only in MLOG mode)
        '''
        val = str(float(self._visainstrument.ask('FREQ:STOP?')))
        return val
    def do_set_stop_freq(self,stop_freq, ):
        '''
        #Setting stop frequency for frequency sweep measurement (Active only in MLOG mode)
        '''
        self._visainstrument.write('FREQ:STOP {stop_freq}'.format(stop_freq=stop_freq,))

    def do_get_bw(self):
        '''
        # Bandwidth selection in kHz - select the widest bandwidth compatible with your measurement
        '''
        val = str(float(self._visainstrument.ask('SENS1:BAND:RES?')))
        return val
    def do_set_bw(self,BW, ):
        '''
        # Bandwidth selection in kHz - select the widest bandwidth compatible with your measurement
        '''
        self._visainstrument.write('SENS1:BAND:RES {BW}'.format(BW=BW,))
    
    def do_get_source_power(self):
        '''
        # Getting source power in dBm (available from -30dBm to 10dBm)
        '''
        val = str(float(self._visainstrument.ask('SOUR:POW?')))
        return val
    def do_set_source_power(self,source_power, ):
        '''
        # Setting source power in dBm (available from -30dBm to 10dBm)
        '''
        self._visainstrument.write('SOUR:POW {source_power}'.format(source_power=source_power,))

    def do_get_vna_mode(self):
        '''
        # Getting VNA mode (LIN - Linear frequency sweep at constant source power, LOG -  logarithmic frequency sweep, SEG - segmented frequency sweep, 
        POW - power sweep, CW - time sweep, POIN - CW mode sweep )
        '''
        val = self._visainstrument.ask('SENS:SWE:TYPE?').rstrip('\n')
        return val
    def do_set_vna_mode(self,vna_mode, ):
        '''
        # Choosing VNA mode (LIN - Linear frequency sweep at constant source power, LOG -  logarithmic frequency sweep, SEG - segmented frequency sweep, 
        POW - power sweep, CW - time sweep, POIN - CW mode sweep )
        '''
        if vna_mode.upper() in ('LIN','LOG','SEG','POW','POIN','CW'):
            vna_mode = vna_mode.upper()
        else:
            raise ValueError("VNA mode can only LIN - Linear frequency sweep at constant source power, LOG -  logarithmic frequency sweep, SEG - segmented frequency sweep, POW - power sweep  ")
        self._visainstrument.write('SENS:SWE:TYPE {vna_mode}'.format(vna_mode=vna_mode,))
    

    def do_get_data_format(self):
        '''
        # Setting up data format on y axes (MLIN - linear mag, MLOG - magnitude in dB, PHAS - Phase in deg, UPH - unwrapped phase in deg)
        '''
        val = (self._visainstrument.ask('CALC:FORM?')).rstrip('\n')
        return val

    def do_set_data_format(self,data_format, ):
        '''
        # Setting up data format on y axes (MLIN - linear mag, MLOG - magnitude in dB, PHAS - Phase in deg, UPH - unwrapped phase in deg)
        '''
        if data_format.upper() in ('MLIN','MLOG','PHAS','UPH'):
            data_format = data_format.upper()
        else:
            raise ValueError("Data format can only be among MLIN - linear mag, MLOG - magnitude in dB, PHAS - Phase in deg, UPH - unwrapped phase in deg")
        self._visainstrument.write('CALC:FORM {data_format}'.format(data_format=data_format,))
    def do_set_averaging_count(self,averaging_count):
        '''
        Sets the averaging count
        '''
        self._visainstrument.write('SENS1:AVER:COUN {averaging_count}'.format(averaging_count=averaging_count))
    def do_get_averaging_count(self):
        '''
        Gets the averaging count
        '''
        count = int(self._visainstrument.ask('SENS1:AVER:COUN?'))
        return count
    #def do_get_meas_param(self):
    #    '''
    #        Gets the measurement parameter: S11,S12,S21,S22
    #    '''
    #    param = str(self._visainstrument.write('CALCULATE1:PARAMETER:SDEFINE "Trc1"?'))
    #    return param
    def do_set_meas_param(self, meas_param):
        if meas_param.upper() in ('S11','S12','S21','S22',):
            meas_param = meas_param.upper()
        else:
            raise ValueError("Measurement parameter can only be  S11,S12,S21,S22.")
        self._visainstrument.write('CALCULATE1:PARAMETER:SDEFINE "Trc1", "{meas_param}"'.format(meas_param=meas_param,))

    def set_param_active(self,):
        '''
        # Choosen parameter set to active
        '''
        self._visainstrument.write('CALCULATE1:PARAMETER:SELECT "Trc1"')
    def set_display_param(self,):
        '''
        # Show choosen parameter on display
        '''
        self._visainstrument.write('DISPLAY:WINDOW1:TRACE5:FEED "Trc1"')

    def set_averaging_on(self):
        '''
        # Number of consecutive sweeps to be combined for the sweep average, average ON /OFF, clearing average, 
        # There is also an option Smoothing - averaging between adjacent sweep points in percentage of overall num of points
        '''

        Averaging = 'ON'
        self._visainstrument.write('SENS1:AVER {Averaging}; CLE'.format(Averaging=Averaging,))

    def set_averaging_off(self):
        '''
        # Number of consecutive sweeps to be combined for the sweep average, average ON /OFF, clearing average, 
        # There is also an option Smoothing - averaging between adjacent sweep points in percentage of overall num of points
        '''
        Averaging = 'OFF'
        self._visainstrument.write('SENS1:AVER {Averaging}; CLE'.format(Averaging=Averaging,))


    def _write(self,com):
        self._visainstrument.write(com)
        
    def _clear(self):
        return self.lib.clear(self._visainstrument.session)  
        
    def _query_trace(self):
        x = self._visainstrument.query_ascii_values('TRAC:STIM? CH1DATA', converter='f')    # Trace stimulus (x axes) readout 
        y = self._visainstrument.query_ascii_values('CALC:DATA? FDAT', converter='f')       # Trace values (y axes) readout 
        return x,y
        
            
           
    ## USER function for getting measurement average as single point             
    def get_point(self):
        logging.info(__name__ + ' : Getting data from instrument directly - returning as one point')
        self._visainstrument.write('INIT1:IMM; *OPC?')                                      # Initiating measurement and waiting till measurement is done
        trace = self._visainstrument.query_ascii_values('CALC:DATA? FDAT', converter='f')   # Trace readout, not using _query_trace because of speed
        #self._visainstrument.write('SENS1:AVER:CLE;')                       # Clearing previous average
        return float(sum(trace)/len(trace))                                                # Computing average value of full trace and returning one point
        
        
    ## USER function for getting full trace with stimulus (x axes) values            
    def get_trace(self):
        logging.info(__name__ + ' : Getting data from instrument indirectly - returning whole trace')
        self._visainstrument.write('INIT1:IMM; *OPC?')                       # Initiating measurement and waiting till measurement is done
        (x,y) = self._query_trace()
        #self._visainstrument.write('SENS1:AVER:CLE;')                       # Clearing previous average

        yunits = self.do_get_data_format()
        xunits = self.do_get_vna_mode()
        if xunits == 'CW' or xunits == 'POIN':
            xunits = 'Time [s]'
        else:
            xunits = 'Frequency [Hz]'
        
        plt.plot(x, y, 'k')
        plt.title(' VNA_trace_readout')
        plt.xlabel(xunits)
        plt.ylabel(yunits)
        plt.grid()
        plt.show()
        return (x,y)                                                        # Return value is a tuple with trace x axes as first and trace y axes as second value  
                                                               
    