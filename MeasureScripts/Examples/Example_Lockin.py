from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) LOCKIN MEASUREMENT
#####################################################
IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')   # Initialize dmm
UHFLI_lib.UHF_init_demod()  # Initialize UHF LI

gain = 1e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
gain_Lockin = 1e6 # Conversion factor for the Lockin

# Sweeping vector
v_vec = arange(-5,5,2)  ''' !! Take care about step sign '''


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

data = qt.Data(name=' testmeasurement')  # Put one space before name


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data.add_coordinate('Voltage [mV]')   # Underline makes the next letter as index

data.add_value('AC Conductance')      # Underline makes the next letter as index

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Getting filepath to the data file
data_path = data.get_dir() 

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d_lockin = qt.Plot2D(data, name='lockin', autoupdate=False)
plot2d_lockin.set_style('lines')



# preparation is done, now start the measurement.
# IVVI.set_dac1(bias)
# It is actually a simple loop.
start = time()
for v in v_vec:
    # set the voltage
    IVVI.set_dac1(v)

    # readout form UHFLI
    # argument Num_of_TC represents number of time constants to wait before raeding the value
    # it is important because of the settling time of the low pass filter
    result_lockin = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)/gain_Lockin  # Reading the lockin and correcting for M1b gain

    # save the data point to the file
    data.add_data_point(v, result_lockin)  

    plot2d_lockin.update()

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
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
