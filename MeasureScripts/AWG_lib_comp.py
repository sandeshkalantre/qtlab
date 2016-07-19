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



def set_waveform(seq,AWG_clock,AWGMax_amp, sync = None, compensate = None, t_sync = 2):
    '''
    This function uploads and loads previously created sequence to the AWG. 
       
        
        Input:
            seq (list) : list of sequences for every channel
            AWG_clock (int) : AWG clock
            AWGMax_amp : # In Volts!!! Maximum needed amplitude on all channels for your particular experiment (noise reduction) 
            sync (Waveform object) : Synchronization element of sequence
            t_sync (float) = Duration of synchronization element of sequence, in TimeUnits
            compensate (Waveform object) : Compensate (for mean value) element of sequence
                      
            
        Output:
            None
        '''
    
   
    if (sync == None) or (compensate == None):
        raise Exception("Sync and compensate sequence elements not created")

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
        for seq_elem in seq[ch_num]:
            if ch_num == 0:   # Sequence for all channels have same length so we need to take a look at just one
                time_seq = time_seq + sum(seq_elem.timings.values())
                weigths.append(sum(seq_elem.timings.values()))   # Storing complete time of single element in sequence 
            aver_list[ch_num].append(seq_elem.waveform.mean())  # Adding average for every element of one channel in the sequence
        aver_list[ch_num] = np.average(aver_list[ch_num], weights=weigths)
        

    print ("aver_list",aver_list)
    print ("time_seq",time_seq)

   
    # Compensation element calculation principle:
    # First calculate compensation element time based on sequence area and AWGMax_amp using formula: time_comp = area/AWGMax_amp , for all channels
    # Find maximum compensation element time of all channels and set compensation element time time_comp to that one
    # For each channel calculate amplitude of compensation element amp_comp based on time_comp, formula: amp_comp = (mean value*overall sequence time)/time_comp - line 103
    # Reason for this approach is AWG requirement that all channels need to have same number of points - compensation element time need to be the same for all channels

    # Calculating compensation element time
    time_comp = 0 # Time of compensation element
    for ch_num in xrange(len(seq)):
        AWGMax_amp_real_units = AWGMax_amp/(seq[ch_num][0].AmpUnitsDict[seq[ch_num][0].AmpUnitsKey])  # Converting AWGMax_amp to real units for sequence for each channel
        time_comp_temp = abs(((aver_list[ch_num] * time_seq)/AWGMax_amp_real_units))  # Calculating time of compensation element with amplitude equal to AWGMax_amp_real_units
        if time_comp_temp > time_comp:  # Finding biggest time of compensation element amongst all channels (needed becuse sequences for all channels need to be of the same length)
            time_comp = time_comp_temp

    time_comp = time_comp*5 + 1 # Increasing time of compensation element to achieve lower compensation amplitude, adding one to avoid zero value

    print ("time_comp",time_comp) 
    

    # Creating two first elements in sequence - sync and compensate
    for ch in xrange(len(seq)):
        
         
        amp_comp = -(aver_list[ch]*time_seq)/time_comp # If mean value of sequence is positive, amplitude of compensation pulse needs to be negative and vice versa


        print ("amp_comp", amp_comp)

        if 'CH1' in seq[ch][0].waveform_name:   # Checking for which channel sync and compensate elements needs to be created
                                                 # by checking the name of first element dedicated to specified channel

            sync.setValuesCH1([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH1([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons

            compensate.setValuesCH1([time_comp,amp_comp])  # Second element in list with calculated amplitude for compensation reasons
            compensate.setMarkersCH1([0],[0])   # Second element in list for compensation reasons, with zero marker amp

        elif 'CH2' in seq[ch][0].waveform_name:
            sync.setValuesCH2([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH2([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons

            compensate.setValuesCH2([time_comp,amp_comp])  # Second element in list with calculated amplitude for compensation reasons
            compensate.setMarkersCH2([0],[0])   # Second element in list for compensation reasons, with zero marker amp

        elif 'CH3' in seq[ch][0].waveform_name:
            sync.setValuesCH3([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH3([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons

            compensate.setValuesCH3([time_comp,amp_comp])  # Second element in list with calculated amplitude for compensation reasons
            compensate.setMarkersCH3([0],[0])   # Second element in list for compensation reasons, with zero marker amp

        elif 'CH4' in seq[ch][0].waveform_name:
            sync.setValuesCH4([t_sync,0])  # Starting element in sequence with zero amp for synchronization reasons
            sync.setMarkersCH4([0],[0])   # Starting element in sequence with zero marker amp for synchronization reasons

            compensate.setValuesCH4([time_comp,amp_comp])  # Second element in list with calculated amplitude for compensation reasons
            compensate.setMarkersCH4([0],[0])   # Second element in list for compensation reasons, with zero marker amp



    # Adding sync and compensate elements at the start of the sequence
    for ch in xrange(len(seq)):

        if 'CH1' in seq[ch][0].waveform_name:
            if time_comp == 0:   # If time of compensation element is zero -> mean value is zero -> no need for compensation element -> not putting it in the list below
                seq[ch] = [sync.CH1] + seq[ch]
            else:               # If time of compensation element is nonzero -> compensation element is needed
                seq[ch] = [sync.CH1, compensate.CH1] + seq[ch]

        elif 'CH2' in seq[ch][0].waveform_name:
            if time_comp == 0:   # If time of compensation element is zero -> mean value is zero -> no need for compensation element -> not putting it in the list below
                seq[ch] = [sync.CH2] + seq[ch]
            else:               # If time of compensation element is nonzero -> compensation element is needed
                seq[ch] = [sync.CH2, compensate.CH2] + seq[ch]
            
        elif 'CH3' in seq[ch][0].waveform_name:
            if time_comp == 0:   # If time of compensation element is zero -> mean value is zero -> no need for compensation element -> not putting it in the list below
                seq[ch] = [sync.CH3] + seq[ch]
            else:               # If time of compensation element is nonzero -> compensation element is needed
                seq[ch] = [sync.CH3, compensate.CH3] + seq[ch]
             
        elif 'CH4' in seq[ch][0].waveform_name:
            if time_comp == 0:   # If time of compensation element is zero -> mean value is zero -> no need for compensation element -> not putting it in the list below
                seq[ch] = [sync.CH4] + seq[ch]
            else:               # If time of compensation element is nonzero -> compensation element is needed
                seq[ch] = [sync.CH4, compensate.CH4] + seq[ch]
            
       

    
 
    
    ## UPLOAD Sequence to AWG hard
    for ch_num in xrange(len(seq)):
        for seq_elem in seq[ch_num]:
            #seq_elem.rescaleAmplitude(AWGMax_amp, mean = aver_list[ch_num])
            seq_elem.rescaleAmplitude(AWGMaxAmp = AWGMax_amp)
            AWG.send_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            AWG.import_waveform_object(Wav = seq_elem, path = 'C:\SEQwav\\')
            
            
    
    ## SET AWG
    AWG.set_sequence_mode_on()  # Tell the device to run in sequence mode (run_mode_sequence)
    AWG.set_seq_length(0)   # Clear all elements of existing sequence   
    AWG.set_seq_length(len(seq[0]))  # Sequence length is number of elements in already created sequence
                                     # Same for all channels
    
    
    seq = filter(None, seq)  # Remove all empty elements from list


    # Create the sequence from previously uploaded files for wanted channels 
    
    for ch in xrange(len(seq)):   # Iterating trough channels
        print "Loading %d" %ch
        
        if 'CH1' in seq[ch][0].waveform_name:   # Checking to which channel sequence elements needs to be uploaded
            channel = 1                        # by checking the name of first element dedicated to specified channel
        elif 'CH2' in seq[ch][0].waveform_name:
            channel = 2
        elif 'CH3' in seq[ch][0].waveform_name:
            channel = 3
        elif 'CH4' in seq[ch][0].waveform_name:
            channel = 4

        
        for elem_num,seq_elem in enumerate(seq[ch]):   # Iterating trough sequence elements

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
     
    
    
    
