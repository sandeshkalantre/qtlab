from numpy import pi, random, arange, size
from time import time,sleep


IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM1', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502785::INSTR')  # Initialize dmm
#dmm.set_NPLC = 0.2  # Setting PLCs of dmm

gain = 1e6 # hoose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#1m : 10000
#10mv : 1000
#100mv : 100
lockin_gain = 10000

bias = 100
v_div = 10e-3
print "Bias [mV]", bias*v_div

# Sweeping vector
v_vec = arange(-330,-400,-0.06)  #''' !! Take care about step sign '''


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

data = qt.Data(name='industrial sample 14-15 IVG lockin')  # Put one space before name


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data.add_coordinate('Voltage [mV]')     # Underline makes the next letter as index

data.add_value('Current [pA]')          # Underline makes the next letter as index

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name='measure2D', autoupdate=False)
plot2d.set_style('lines')


# preparation is done, now start the measurement.

# It is actually a simple loop.
IVVI.set_dac1(bias)
start = time()
for v in v_vec:
    # set the voltage
    IVVI.set_dac5(v)

    # readout
    result = dmm.get_readval()/(gain*lockin_gain)*1e12

    # save the data point to the file, this will automatically trigger
    # the plot windows to update
    data.add_data_point(v, result)
    plot2d.update()
    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    qt.msleep(0.1)
stop = time()
print 'Duration: %s sec' % (stop - start, )


   


# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
