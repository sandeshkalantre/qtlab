from numpy import pi, random, arange, size, mod
from time import time,sleep
import datetime
import UHFLI_lib



IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
AWG = qt.instruments.get("AWG")

 



UHFLI_lib.UHF_init_demod(demod_c = 3)  # Initialize UHF LI
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
data = qt.Data(name='5-24 jumptest')


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('Num of samples')

data.add_value('Reflection [Arb. U.]')

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
    plot2d = qt.Plot2D(data, name='noname', autoupdate=False)
    plot2d.set_style('lines')



    
    # readout
    result = UHFLI_lib.UHF_measure_demod_trig(Num_of_TC = 3, trigger = 3, record_time = 5,  AWG_instr = AWG)

    # save the data trace to the file

    data.add_data_point(np.linspace(0, result.size, result.size), result)


    plot2d.update()

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)

finally:


   
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
