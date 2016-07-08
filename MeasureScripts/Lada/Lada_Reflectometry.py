from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) LOCKIN MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')   # Initialize dmm
UHFLI_lib.UHF_init_demod(demod_c = 3)  # Initialize UHF LI

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = 80

leak_test = True

gain_Lockin = 1 # Conversion factor for the Lockin

# Sweeping vector
v_vec = arange(0,4000,0.06)  ##''' !! Take care about step sign '''


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

data_reflectometry = qt.Data(name='5-24 manually set stuff+trigger -45dBm, 1Mhz (2), 80uV')  # Put one space before name
#data_current = qt.Data(name='5-24 current vs sensor gate')  # Put one space before name



# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data_reflectometry.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_reflectometry.add_value(' Reflection [Arb. U.]')      # Underline makes the next letter as index

#data_current.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

#data_current.add_value(' Current [pA]')      # Underline makes the next letter as index

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data_reflectometry.create_file()
#data_current.create_file()

# Getting filepath to the data file
data_path = data_reflectometry.get_dir() 

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d_relflectometry = qt.Plot2D(data_reflectometry, name='reflection10', autoupdate=False)
plot2d_relflectometry.set_style('lines')

#plot2d_current = qt.Plot2D(data_current, name='current', autoupdate=False)
#plot2d_current.set_style('lines')



# preparation is done, now start the measurement.
IVVI.set_dac1(bias)
# It is actually a simple loop.
start = time()
for v in v_vec:
    # set the voltage
    IVVI.set_dac8(v)

    # readout form UHFLI
    # argument Num_of_TC represents number of time constants to wait before raeding the value
    # it is important because of the settling time of the low pass filter
    result_reflectometry = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)  # Reading the lockin and correcting for M1b gain
    #result_current = dmm.get_readval()/gain*1e12
    # save the data point to the file
    data_reflectometry.add_data_point(v, result_reflectometry) 
    #data_current.add_data_point(v, result_current) 

    if leak_test:
        #plot2d_current.update()
        plot2d_relflectometry.update()   # If leak_test is True update every point 
    elif not bool(mod(v,50)):  
        #plot2d_current.update()  
        plot2d_relflectometry.update()   # Update every 10 points

    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    qt.msleep(0.001)
stop = time()
print 'Duration: %s sec' % (stop - start, )

# Saving UHFLI setting to the measurement data folder
# You can load this settings file from UHFLI user interface 
UHFLI_lib.UHF_save_settings(path = data_path)


# after the measurement ends, you need to close the data file.
data_reflectometry.close_file()
#data_current.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
