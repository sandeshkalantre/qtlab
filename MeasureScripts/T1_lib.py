import Tektronix_AWG5014 as ArbWG
import InverseHPfilterSeq as INV   # ADDED
import matplotlib.pyplot as plt
import qt
import re
import time
import warnings
import itertools
import numpy as np 

import zhinst.utils as utils
import zhinst.ziPython as ziPython



if 'AWG' in locals():
    AWG._ins._visainstrument.close()   # Trying to close previous AWG session. 

       
AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', address='169.254.111.236')



def set_waveform(seq,AWG_clock,AWGMax_amp,Seq_length):
    
   
    AWG.set_ch1_amplitude(AWGMax_amp)  # Setting maximum needed amp on all channels
    AWG.set_ch2_amplitude(AWGMax_amp) 
    AWG.set_ch3_amplitude(AWGMax_amp) 
    AWG.set_ch4_amplitude(AWGMax_amp) 
   
        
    AWG.del_waveform_all()  # Clear all waveforms in waveform list
    AWG.set_clock(AWG_clock)  # Set AWG clock


    ## Making HP inverse on CH1      # ADDED
    #CompleteSeqWav = np.array([])
    #for index, elem in enumerate(seq[0]):    # Creating single array with all sequence wavefroms concatenated
     #   CompleteSeqWav = np.concatenate((CompleteSeqWav,np.array(elem.waveform)))
        
    #CompleteSeqWavInv = INV.InverseHPfilterSeq(CompleteSeqWav, R = 2E7, C = 1E-9)   # Making HP inverse on concatenated wavefroms
   # 
  # 
    #print(len(CompleteSeqWav), len(CompleteSeqWavInv))
    #
    #stop = 0 
    #for index, elem in enumerate(seq[0]):  # Slicing HP inverted concatenated wavefroms back into sequnce elements
    #    start = stop 
    #    stop = start + len(elem.waveform)
    #    elem.waveform = CompleteSeqWavInv[start:stop]
    
    #plt.figure("WAVEFORM_INVERTED")
    #plt.plot(seq[0][2].waveform)
    #plt.show()
    
    #print("Lch1",len(seq[0][2].waveform),"Lch2",len(seq[1][2].waveform))
    
    
    
    ## UPLOAD Sequence to AWG hard
    for ch_num in xrange(len(seq)):
        for seq_elem in seq[ch_num]:
            seq_elem.rescaleAmplitude(AWGMax_amp)
            AWG.send_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            AWG.import_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            
            
    
    ## SET AWG
    AWG.set_sequence_mode_on()  # Tell the device to run in sequence mode (run_mode_sequence)
    AWG.set_seq_length(0)   # Clear all elements of existing sequence   
    AWG.set_seq_length(Seq_length)  # Set wanted sequence length
    
    
    # Create the sequence from previously uploaded files for wanted channels 
    
    for ch_num in xrange(len(seq)):   # Iterating trough channels
        for elem_num, seq_elem in enumerate(seq[ch_num]):   # Iterating trough sequence elements
            
            #if elem_num == 0: # If it is the FIRST element set TWAIT = 1 - wait for trigger
                #AWG.load_seq_elem(elem_num+1,ch_num+1, seq_elem.waveform_name, TWAIT = 1)
                
            if elem_num == (len(seq[ch_num])-1): # If it is the last element set GOTOind=1 - return to first elem
                AWG.load_seq_elem(elem_num+1,ch_num+1, seq_elem.waveform_name, GOTOind=1)
                
            else:
                AWG.load_seq_elem(elem_num+1,ch_num+1, seq_elem.waveform_name)
                
               
                           
    #Turn on the AWG channels
    AWG._ins.do_set_output(1,1)
    AWG._ins.do_set_output(1,2)
    #AWG._ins.do_set_output(1,3)
    #AWG._ins.do_set_output(1,4)
    
    
    
    #Run
    AWG.run()
     
    
    
    
def UHF_measure(device_id = 'dev2148', maxtime = 5):
    
    """
    Connecting to the device specified by device_id and obtaining
    demodulator data using ziDAQServer's blocking (synchronous) poll() command

   

    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      maxtime (int): Maximum measurement time in seconds - after this 
        period expires measurement is stopped and data collected until that
        point is returned

    Returns:

      shotCH1,shotCH2 (np.array)  -  vectors of data read out on channels CH1 and CH2

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """
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

    AWG.force_trigger() # This trigger also triggers lockin aquisition/BNC cable
    
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
    

    
            


