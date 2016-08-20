from numpy import pi, random, arange, size
from time import time,sleep

dmm = qt.instruments.create('dmm','Keithley_2000', address = 'GPIB::16::INSTR')  # Initialize dmm


dummy_vec = np.linspace(0,1000,100)
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

data = qt.Data(name='dmm_test')  # Put one space before name


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data.add_coordinate('Voltage [mV]')     # Underline makes the next letter as index
data.add_value('Voltage [V]')          # Underline makes the next letter as index

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
start = time()
for v in dummy_vec:
    

    # readout
    result = dmm.get_readval()

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