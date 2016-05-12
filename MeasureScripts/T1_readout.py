import T1_lib
reload(T1_lib)
import Waveform_PresetAmp as Wav
import numpy as np
#import qt
import matplotlib.pyplot as plt

### UHF LI READOUT
##

#d = qt.Data()
#d.add_coordinate('X')
#d.add_value('Y')
#d.create_file()
#p = plot(d)

# Inform wrapper that a measurement has started
#qt.mstart()

shotCH1,shotCH2 = T1_lib.UHF_measure()  # Reading out UHF LI scope shot. Channel one data in shotCH1, channel two data in shotCH2
#plt.plot(shotCH1)

#y = shotCH2
#x = np.linspace(1, len(y), len(y))
#d.add_data_point(x, y)
#p.set_xrange(0, len(y))
#qt.msleep(0.1)

# Inform wrapper that the measurement has ended
#d.close_file()
#qt.mend()