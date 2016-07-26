from numpy import pi, random, arange, size, mod, reshape, mean
from time import time,sleep
import datetime
import UHFLI_lib
import matplotlib.pyplot as plt
import math


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
AWG = qt.instruments.get("AWG")
#name='pulsing,80uV -35dBm, -+500, +-600, 200us200us three-part-pulse 1000#' 
name = "5-24 By=2T,crazy sequence, W,L,W,R,E 700us"

Scope_sampling_rate =  7030000#Hz
Sequence_duration = 0.5065 #s
Num_of_pulses = 100 # Sequence length - correspond to number of rows in slice matrix

Signal_level = 0.0015 # In Volts. AWG Marker level 

 



UHFLI_lib.UHF_init_scope()  # Initialize UHF LI
# you indicate that a measurement is about to start and other
# processes should stop (like batterycheckers, or temperature
# monitors)
qt.mstart()

# Next a new data object is made.
# The file will be placed in the folder:
# <datadir>/<datestamp>/<timestamp>_testmeasurement/
# and will be called:
# <timestamp>_testmeasurement.dat
# to find out what 'datadir' is set to, type: qt.config.get('datadir')
data = qt.Data(name=name)


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('Line_num')
data.add_coordinate('Num of samples')
data.add_value('Reflection [Arb. U.]')
#data.add_value('Pulse Voltage [V]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

try:
    data_path = data.get_dir()

    # Next two plot-objects are created. First argument is the data object
    # that needs to be plotted. To prevent new windows from popping up each
    # measurement a 'name' can be provided so that window can be reused.
    # If the 'name' doesn't already exists, a new window with that name
    # will be created. For 3d plots, a plotting style is set.
    plot3d = qt.Plot3D(data, name='crazy_seq1', coorddims=(0,1), valdim=2, style='image', autoupdate = False)
    #plot2d = qt.Plot2D(data, name=name, autoupdate=True)
    #plot2d.set_style('lines')

    #AWG._ins.stop()
    AWG._ins.run()  # Run AWG - Run must be before do_set_output
    AWG._ins.do_set_output(1,1)   # Turn on AWG ch1
    AWG._ins.do_set_output(1,2)   # Turn on AWG ch1



    # readout
    result = UHFLI_lib.UHF_measure_scope(AWG_instance = AWG, maxtime = 2)

    # Turn off AWG
    #AWG._ins.do_set_output(0,1)   # Turn on AWG ch1
    #AWG._ins.stop()

    # save the data trace to the file

    #data.add_data_point(np.linspace(0, result[0].size, result[0].size), result[0], result[1])




    #plot2d.update()

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)
    

    #ch2 = result[1] # Readout form scope channel two (AWG Marker1)
    #ch2 = ch2[::-1] # Reversing ch2 for argmax function
    #Signal_level = abs(Signal_level)/2 # DIvision by two because of 50ohm UHFLI input termination
    #ch2 = abs(ch2)
    #end_index = - np.argmax(ch2>Signal_level*0.8) # Ending index of readout data is when Marker becomes high, minus sign because of reversed ch2 vector, factor 0.8 to be sure to catch something
    length_fixed = Scope_sampling_rate*Sequence_duration - (Scope_sampling_rate*Sequence_duration)%Num_of_pulses
    length_fixed = int(length_fixed)
    num_col = length_fixed /Num_of_pulses

     
    ch1 = result[0]#[0:end_index] # Reducing redout data on scope ch1 to Sequence length (Marker length) 
    #num_col = float(ch1.size)/Num_of_pulses # Rounded integer value (to lower) of columns in slice matrix
    #num_col = math.trunc(num_col)
    #Num_of_pulses += 1
    ch1 = ch1[0:num_col*Num_of_pulses] # Cutting ch1 to element number of num_col*Num_of_pulses needed for proper reshaping into slice matrix
    ch1mat = reshape(ch1,(Num_of_pulses, num_col)) # Creating slice matrix
    #pl = plt.plot(ch1mat[0])
    #mean = ch1mat.mean(0)
    #pl = plt.plot(mean)

    for line_num,line in enumerate(ch1mat): # Savig the data slice by slice from slice matrix
        #pulse_middle_amp = seq[0][line_num+1].amplitudes.values()[1][1]# Getting middle pulse amplitude of AWG ch1 (dot) element of the sequence   
        data.add_data_point(np.linspace(line_num, line_num, line.size), np.linspace(0, line.size, line.size), line)
        #data.add_data_point(np.linspace(pulse_middle_amp, pulse_middle_amp, line.size), np.linspace(0, line.size, line.size), line)
        data.new_block()
    
    plot3d.update()

    #plt.show()



finally:
    AWG._ins.do_set_output(0,1)   # Turn off AWG ch1
    AWG._ins.do_set_output(0,2)   # Turn off AWG ch1

   
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
