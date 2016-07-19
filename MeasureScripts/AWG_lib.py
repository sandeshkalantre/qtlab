# 04.05.2016. Added lines 82 to 89 - Uploading sequence to specified channel recognition


#import Tektronix_AWG5014 as ArbWG
#import InverseHPfilterSeq as INV   # ADDED
import matplotlib.pyplot as plt
import qt
import re
import time
import warnings
import itertools
import numpy as np 





#if 'AWG' in locals():
    #AWG._ins._visainstrument.close()   # Trying to close previous AWG session. 

       
#AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', address='169.254.111.236')  # Changed
AWG = qt.instruments.get("AWG")



def set_waveform(seq,AWG_clock,AWGMax_amp, t_sync, sync):

    '''
    This function uploads and loads previously created sequence to the AWG. 
       
        
        Input:
            seq (list) : list of sequences for every channel
            AWG_clock (int) : AWG clock
            AWGMax_amp : # In Volts!!! Maximum needed amplitude on all channels for your particular experiment (noise reduction) 
            sync (Waveform object) : Synchronization element of sequence
            t_sync (float) = Duration of synchronization element of sequence, in TimeUnits
                      
            
        Output:
            None
    '''
    
   
    AWG.set_ch1_amplitude(AWGMax_amp)  # Setting maximum needed amp on all channels
    AWG.set_ch2_amplitude(AWGMax_amp) 
    AWG.set_ch3_amplitude(AWGMax_amp) 
    AWG.set_ch4_amplitude(AWGMax_amp) 
   
        
    AWG.del_waveform_all()  # Clear all waveforms in waveform list
    AWG.set_clock(AWG_clock)  # Set AWG clock


    # Calculate average of whole sequence and sequence length
    aver_list = list()  # List for storing average value of whole sequence for all channels
    weigths = list()  # List containing timings of all elements in the sequence - needed for calculation of weigthed average
    time_seq =  0 # Sequence time
    for ch_num in xrange(len(seq)):
        aver_list.append([])   # Adding element for the channel
        for i,seq_elem in enumerate(seq[ch_num]):
            if ch_num == 0:   # Sequence for all channels have same length so we need to take a look at just one
                time_seq = time_seq + sum(seq_elem.timings.values())
                weigths.append(sum(seq_elem.timings.values()))   # Storing complete time of single element in sequence 
            aver_list[ch_num].append(seq_elem.waveform.mean())  # Adding average for every element of one channel in the sequence
        aver_list[ch_num] = np.average(aver_list[ch_num], weights=weigths)
        

    print ("aver_list",aver_list)
    print ("time_seq",time_seq)

    # Creating first elements in sequence - sync 
    for ch in xrange(len(seq)):
        
        if 'CH1' in seq[ch][0].waveform_name:   # Checking for which channel sync elements need to be created
                                                 # by checking the name of first element dedicated to specified channel

            sync.setValuesCH1([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH1([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons
            seq[ch] = [sync.CH1] + seq[ch] # Adding sync element at the start of the sequence
           

        elif 'CH2' in seq[ch][0].waveform_name:
            sync.setValuesCH2([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH2([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons
            seq[ch] = [sync.CH2] + seq[ch]
           

        elif 'CH3' in seq[ch][0].waveform_name:
            sync.setValuesCH3([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH3([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons
            seq[ch] = [sync.CH3, compensate.CH3] + seq[ch]
           

        elif 'CH4' in seq[ch][0].waveform_name:
            sync.setValuesCH4([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH4([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons
            seq[ch] = [sync.CH4, compensate.CH4] + seq[ch]
           


    
    
    
    ## UPLOAD Sequence to AWG hard
    for ch_num in xrange(len(seq)):
        for i,seq_elem in enumerate(seq[ch_num]):
            if i == 0:   # Skiping substraction of mean value from the sync element
                mean = 0
            else:
                mean = aver_list[ch_num]
            seq_elem.rescaleAmplitude(AWGMax_amp, mean)
            AWG.send_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            AWG.import_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            
            
    
    ## SET AWG
    AWG.set_sequence_mode_on()  # Tell the device to run in sequence mode (run_mode_sequence)
    AWG.set_seq_length(0)   # Clear all elements of existing sequence   
    AWG.set_seq_length(len(seq[0]))  # Set wanted sequence length
    
    
    seq = filter(None, seq)  # Remove all empty elements from list

    # Create the sequence from previously uploaded files for wanted channels 
    
    for ch in xrange(len(seq)):   # Iterating trough channels
        
        if 'CH1' in seq[ch][0].waveform_name:   # Checking to which channel sequence elements needs to be uploaded
            channel = 1                        # by checking the name of first element dedicated to specified channel
        elif 'CH2' in seq[ch][0].waveform_name:
            channel = 2
        elif 'CH3' in seq[ch][0].waveform_name:
            channel = 3
        elif 'CH4' in seq[ch][0].waveform_name:
            channel = 4

        for elem_num, seq_elem in enumerate(seq[ch]):   # Iterating trough sequence elements
            
            if elem_num == 0: # If it is the FIRST element set TWAIT = 1 - wait for trigger
                AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name, TWAIT = 1)


            

            if elem_num == (len(seq[ch])-1): # If it is the last element set GOTOind=1 - return to first elem
                AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name, GOTOind=1)
                
            else:
                AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name)
                
               
                           
    #Turn on the AWG channels
    #AWG._ins.do_set_output(1,1)
    #AWG._ins.do_set_output(1,2)
    #AWG._ins.do_set_output(1,3)
    #AWG._ins.do_set_output(1,4)
    
    
    
    #Run
    #AWG.run()
     
    
    
    
