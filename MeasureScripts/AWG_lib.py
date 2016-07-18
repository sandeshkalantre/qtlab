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



def set_waveform(seq,AWG_clock,AWGMax_amp):
    
   
    AWG.set_ch1_amplitude(AWGMax_amp)  # Setting maximum needed amp on all channels
    AWG.set_ch2_amplitude(AWGMax_amp) 
    AWG.set_ch3_amplitude(AWGMax_amp) 
    AWG.set_ch4_amplitude(AWGMax_amp) 
   
        
    AWG.del_waveform_all()  # Clear all waveforms in waveform list
    AWG.set_clock(AWG_clock)  # Set AWG clock

    
    
    
    ## UPLOAD Sequence to AWG hard
    for ch_num in xrange(len(seq)):
        for seq_elem in seq[ch_num]:
            seq_elem.rescaleAmplitude(AWGMax_amp)
            AWG.send_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            AWG.import_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            
            
    
    ## SET AWG
    AWG.set_sequence_mode_on()  # Tell the device to run in sequence mode (run_mode_sequence)
    AWG.set_seq_length(0)   # Clear all elements of existing sequence   
    AWG.set_seq_length(len(seq[0])  # Set wanted sequence length
    
    
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
            
            #if elem_num == 0: # If it is the FIRST element set TWAIT = 1 - wait for trigger
                #AWG.load_seq_elem(elem_num+1,channel, seq_elem.waveform_name, TWAIT = 1)


            

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
     
    
    
    
