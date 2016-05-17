import matplotlib.pyplot as plt
import qt
import re
import time
import warnings
import itertools
import numpy as np 

import zhinst.utils as utils
import zhinst.ziPython as ziPython




def UHF_init_scope(device_id = 'dev2148'):
    
    """
    Connecting to the device specified by device_id and setting initial parameters 
    


    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, 'dev2148'.



    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    global daq  # Creating global variable for accesing the UHFLI from other functions
    global device # Creating global variable for accesing the UHFLI from other functions 

    # Create an instance of the ziDiscovery class.
    d = ziPython.ziDiscovery()

    # Determine the device identifier from it's ID.
    device = d.find(device_id).lower()

    # Get the device's default connectivity properties.
    props = d.get(device)

    # The maximum API level supported by this example.
    apilevel_example = 5
    # The maximum API level supported by the device class, e.g., MF.
    apilevel_device = props['apilevel']
    # Ensure we run the example using a supported API level.
    apilevel = min(apilevel_device, apilevel_example)
    # See the LabOne Programming Manual for an explanation of API levels.

    # Create a connection to a Zurich Instruments Data Server (an API session)
    # using the device's default connectivity properties.
    daq = ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)

    # Check that the device is visible to the Data Server
    if device not in utils.devices(daq):
        raise RuntimeError("The specified device `%s` is not visible to the Data Server, " % device_id +
                           "please ensure the device is connected by using the LabOne User Interface " +
                           "or ziControl (HF2 Instruments).")

    # find out whether the device is an HF2 or a UHF
    devtype = daq.getByte('/%s/features/devtype' % device)
    options = daq.getByte('/%s/features/options' % device)

    
 

    # Create a base configuration: disable all outputs, demods and scopes
    general_setting = [
        ['/%s/demods/*/rate' % device, 0],
        ['/%s/demods/*/trigger' % device, 0],
        ['/%s/sigouts/*/enables/*' % device, 0]]
    if re.match('HF2', devtype):
        general_setting.append(['/%s/scopes/*/trigchannel' % device, -1])
    else:  # UHFLI
        pass
        #general_setting.append(['/%s/demods/*/enable' % device, 0])
        #general_setting.append(['/%s/scopes/*/enable' % device, 0])
    daq.set(general_setting)
    
    
    raw_input("Set the UHF LI parameters in user interface dialog!  Press enter to continue...")  # Wait for user to set the device parametrs from user interface

    







def UHF_measure_scope(device_id = 'dev2148', maxtime = 5):

    """
    Obtaining data from UHF LI using ziDAQServer's blocking (synchronous) poll() command
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init function

   

    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, 'dev2148'.

      maxtime (int): Maximum measurement time in seconds - after this 
        period expires measurement is stopped and data collected until that
        point is returned

    Returns:

      shotCH1,shotCH2 (np.array)  -  vectors of data read out on scope channels CH1 and CH2

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    data = list()
    
    # Poll data parameters
    poll_length = 0.001  # [s]
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True
    
    daq.setInt('/dev2148/scopes/0/enable', 1)  # Enable scope
    time.sleep(0.5)  # Wait for everything to be proper initialized
    
    #START MEASURE
    # Subscribe to the scope data
    path =  '/%s/scopes/0/wave' % (device)  # Device node to acquire data from (this one stands for scope)
    
    daq.sync()
    daq.subscribe(path)

    #AWG.force_trigger() # This trigger also triggers lockin aquisition/BNC cable  # CHANGED
    
    start = time.time()  # Starting time counter
    while True:  # Readout data block by block until whole buffer is read out
        data.append(daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict))  # Readout from subscribed node (scope)
        if bool(data[-1]) == False:  # If the last poll did not returned any data - buffer is empty - transfer is finished
            break
        stop = time.time() # Checking time pass    
        if (stop - start) > maxtime:  # If measurement time is bigger then maxtime - stop it
            break   
    #END OF MEASURE

  
            
    # Unsubscribe from all paths
    daq.unsubscribe('*')
    
    # Disable the scope
    daq.setInt('/dev2148/scopes/0/enable', 0)
    

    if bool(data[0]) == False:  # If no data is returned
        print("NO DATA RETURNED!")
        return (0,0)
        
    
    # HANDLING THE DATA: 
    shots = list() 
    for i in xrange(len(data)):
        if data[i]:  # If specified poll returned something
            shots.append(data[i][path])  # Extracting measured shot or shots from measurement dictionary in data and putting it in "data" as one element in list
            
    shots = list(itertools.chain(*shots)) # Reducing "shots" dimension to 1d
                                          # Shots is list of dictionaries - each dictionary element is one block 
    
    
    shotCH1 = np.array([0])
    shotCH2 = np.array([0])
    
    Amp_scaling_factorCH1 = shots[0]['channelscaling'][0]  # Extracting amplitude scaling factor from read out data dictionary for channel 1 - see output data structure of poll command
    Amp_scaling_factorCH2 = shots[0]['channelscaling'][1]  # Extracting amplitude scaling factor from read out data dictionary for channel 2 - see output data structure of poll command
    
    # If shot is big it is divided in blocks that needs to be connected (concatenated): 
    # For CH1:  
    for block in shots:  # Going trough all blocks in a shot
        shotCH1 = np.concatenate((shotCH1, block['wave'][:,0]))  # Concatenating block to get a shot recorded on device channel 1
    # For CH2:
    CH2_ON = True # Channel 2 on flag - if it is on flag is True
    try:
        dummy = block['wave'][0,1]  # Checking whether this will return error - channel 2 off , or it will not - channel 2 on
    except IndexError: 
        CH2_ON = False     # If Channel 2 is off flag is False
    
    if CH2_ON:
        for block in shots:  # Going trough all blocks in a shot
            shotCH2 = np.concatenate((shotCH2, block['wave'][:,1]))  # Concatenating block to get a shot recorded on device channel 
        
    
    shotCH1 = shotCH1 * Amp_scaling_factorCH1   # Rescaling returned data to get proper values
    shotCH2 = shotCH2 * Amp_scaling_factorCH2
    
    plt.figure(1)
    plt.title("Data from CH1")
    plt.plot(shotCH1) 
    plt.xlabel('Samples')
    plt.ylabel('Amplitude (V)')
    plt.show(block=False)
    
    if CH2_ON:
        plt.figure(2)
        plt.title("Data from CH2")
        plt.plot(shotCH2) 
        plt.xlabel('Samples')
        plt.ylabel('Amplitude (V)')
        plt.show(block=False)
    
    
    #AWG._visainstrument.close()   # Closing the session towards instrument

    return shotCH1,shotCH2   # Returning data vectors for both channels



def UHF_init_demod(device_id = 'dev2148', demod_c = 0, out_c = 0):
    
    """
    Connecting to the device specified by device_id and setting initial parameters
    


    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, 'dev2148'.



    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    global daq  # Creating global variable for accesing the UHFLI from other functions
    global device # Creating global variable for accesing the UHFLI from other functions 

    # Create an instance of the ziDiscovery class.
    d = ziPython.ziDiscovery()

    # Determine the device identifier from it's ID.
    device = d.find(device_id).lower()

    # Get the device's default connectivity properties.
    props = d.get(device)

    # The maximum API level supported by this example.
    apilevel_example = 5
    # The maximum API level supported by the device class, e.g., MF.
    apilevel_device = props['apilevel']
    # Ensure we run the example using a supported API level.
    apilevel = min(apilevel_device, apilevel_example)
    # See the LabOne Programming Manual for an explanation of API levels.

    # Create a connection to a Zurich Instruments Data Server (an API session)
    # using the device's default connectivity properties.
    daq = ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)

    # Check that the device is visible to the Data Server
    if device not in utils.devices(daq):
        raise RuntimeError("The specified device `%s` is not visible to the Data Server, " % device_id +
                           "please ensure the device is connected by using the LabOne User Interface " +
                           "or ziControl (HF2 Instruments).")

    # find out whether the device is an HF2 or a UHF
    devtype = daq.getByte('/%s/features/devtype' % device)
    options = daq.getByte('/%s/features/options' % device)

    
 

    # Create a base configuration: disable all outputs, demods and scopes
    general_setting = [
        ['/%s/demods/*/rate' % device, 0],
        ['/%s/demods/*/trigger' % device, 0],
        ['/%s/sigouts/*/enables/*' % device, 0]]
    if re.match('HF2', devtype):
        general_setting.append(['/%s/scopes/*/trigchannel' % device, -1])
    else:  # UHFLI
        pass
        #general_setting.append(['/%s/demods/*/enable' % device, 0])
        #general_setting.append(['/%s/scopes/*/enable' % device, 0])
    daq.set(general_setting)
    
    
    raw_input("Set the UHF LI parameters in user interface dialog!  Press enter to continue...")  # Wait for user to set the device parametrs from user interface

   
    daq.setInt('/%s/demods/%s/enable' % (device, demod_c) , 1)  # Enable demodulator 1

    daq.setInt('/%s/demods/%s/rate' % (device, demod_c), 1000000) # Set the demodulator sampling rate
    
    
    # Unsubscribe any streaming data
    daq.unsubscribe('*')



    # Path to UHF LI readout node made globally for using in other functions
    global path_demod
    path_demod = '/%s/demods/%d/sample' % (device, demod_c) 


    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers. Note: the sync()
    # must be issued after waiting for the demodulator filter to settle above.
    daq.sync()

    # Subscribe to the demodulator's sample
    path = path_demod
    daq.subscribe(path)

    # Get output amplitude
    global out_ampl 
    out_ampl = daq.getDouble('/%s/sigouts/%s/amplitudes/3' % (device, out_c))/np.sqrt(2)

    # Get time constant in seconds
    TC = daq.getDouble('/%s/demods/%s/timeconstant' % (device, demod_c))
    # Wait for the demodulator filter to settle
    time.sleep(5*TC)

    



    

    
            

def UHF_measure_demod(demod_c = 0, out_c = 0):

    """
    Obtaining data from UHF LI demodulator using ziDAQServer's blocking (synchronous) poll() command
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init function

   

    Arguments:

      demod_c (int): One of {0 - 7} demodulators of UHF LI 
      out_c (int): One of {0,1} output channels of UHF LI

    Returns:

      measured_ac_conductance (float): Division between output voltage RMS value and acqired samples mean value (assumed as current).
        Needs to be corrected with appropriate constant in user script. 

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    
    
    path = path_demod

    # Poll data parameters
    poll_length = 0.001  # [s]
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True 

    

    #START MEASURE

    data = daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)  # Readout from subscribed node (demodulator)
    
    #END OF MEASURE
    

    # Check the dictionary returned is non-empty
    assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
    # Note, the data could be empty if no data arrived, e.g., if the demods were
    # disabled or had demodulator rate 0
    assert path in data, "data dictionary has no key '%s'" % path
    # The data returned is a dictionary of dictionaries that reflects the node's path


    # The data returned is a dictionary of dictionaries that reflects the node's path
    sample = data[path]
    sample_x = np.array(sample['x'])    # Converting samples to numpy arrays for faster calculation
    sample_y = np.array(sample['y'])    # Converting samples to numpy arrays for faster calculation
    sample_r = np.sqrt(sample_x**2 + sample_y**2)   # Calculating R value from X and y values
    
    
    sample_mean = np.mean(sample_r)  # Mean value of recorded data vector
    measured_ac_conductance = out_ampl/sample_mean
  
    return measured_ac_conductance 


