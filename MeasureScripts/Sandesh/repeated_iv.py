from numpy import pi, random, arange, size, mod
from time import time,sleep

qt.config.set('datadir',"C:\QTLab\Measurement_data\Sandesh")


IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM1', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502785::INSTR')

f = open('res_data.txt','a')

while(True):
    gain = 1e4 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    v_vec = arange(-100,100,2)


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
    data = qt.Data(name='IV')


    # Now you provide the information of what data will be saved in the
    # datafile. A distinction is made between 'coordinates', and 'values'.
    # Coordinates are the parameters that you sweep, values are the
    # parameters that you readout (the result of an experiment). This
    # information is used later for plotting purposes.
    # Adding coordinate and value info is optional, but recommended.
    # If you don't supply it, the data class will guess your data format.
    data.add_coordinate('Current [uA]')
    data.add_value('Voltage [V]')

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
    res_vec = []
    start = time()
    for v in v_vec:
        # set the voltage
        IVVI.set_dac1(v)

        # readout
        result = dmm.get_readval()/gain
        res_vec.append(result)
        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(v, result)
        plot2d.update() 

        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.001)
    stop = time()
    print 'Duration: %s sec' % (stop - start, )
    #print res_vec
    resistance = (res_vec[-1] - res_vec[0])/((20e-6))
    print 'Approximate resistance',resistance, "Ohms"
    line = str(time()) + "," + str(resistance) + '\n'
    f.write(line)
    f.flush()

   


    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
f.close()