def InverseHPfilterSeq(X, R,C, F_sample = 10000000, M=None):
    """Filtering on a real signal using inverse FFT
    
    Inputs
    =======
    
    X: 1-D numpy array of floats, the real time domain signal (time series) to be filtered
      
    
    Notes
    =====
    1. The input signal must be real, not imaginary nor complex
    2. The Filtered_signal will have only half of original amplitude. Use abs() to restore. 
    
    
    """        
    
    
    import scipy, numpy, cmath
    import matplotlib.pyplot as plt
    
    if M == None: # if the number of points for FFT is not specified
        M = X.size # let M be the length of the time series

    Spectrum = scipy.fft(X, n=M)  # Multiplying with sum of rectangular time window M, which is also length of the signal  # CHANGED, BEFORE: Spectrum = scipy.fft(X, n=M)
    
    #plt.figure("Spectrum_real")
    #plt.plot(scipy.real(Spectrum))
    #plt.plot(scipy.imag(Spectrum))
    
    
    """
    Generating a transfer function for RC filters.
    Importing modules for complex math and plotting.
    """

    f = numpy.arange(-len(Spectrum)/2,len(Spectrum)/2, 1)
    w = 2.0j*numpy.pi*f


    
    hp_tf = (w*R*C)/(w*R*C+1)  # High Pass Transfer function
    

    right_hp_tf = hp_tf[len(hp_tf)/2:len(hp_tf)]
    right_hp_tf_inv = 1/right_hp_tf[1:len(right_hp_tf)]
    #print("right_hp_tf:  ", len(right_hp_tf))
    #print("right_hp_tf_inv:  ", len(right_hp_tf_inv))
    left_hp_tf = hp_tf[0:len(hp_tf)/2]
    left_hp_tf_inv = 1/left_hp_tf
    #print("left_hp_tf:  ", len(left_hp_tf))
    #print("left_hp_tf_inv:  ", len(left_hp_tf_inv))
    
    
    hp_tf = numpy.concatenate((right_hp_tf,left_hp_tf))
    inv_hp_tf = numpy.concatenate((numpy.array([0]),right_hp_tf_inv,left_hp_tf_inv))
    #print("inv_hp_tf:  ", len(inv_hp_tf))
    
    #plt.figure("RC_real")
    #plt.plot(f, scipy.real((hp_tf))) # plot high pass transfer function
    #plt.figure("RC_imag")
    #plt.plot(f, scipy.imag(hp_tf)) # plot high pass transfer function

    
    
    


    #plt.figure("RCinv_real")
    #plt.plot(f, scipy.real((inv_hp_tf))) # plot high pass transfer function
    #plt.figure("RCinv_imag")
    #plt.plot(f, scipy.imag(inv_hp_tf)) # plot high pass transfer function
    
    #plt.show()



    #Filtered_spectrum = Spectrum*hp_tf  # Filtering with HP
    #Filtered_spectrum = Filtered_spectrum*inv_hp_tf  # Filtering with inverse HP afterwards
    Filtered_spectrum = Spectrum*inv_hp_tf*1./M # Filtering with inverse HP,   # CHANGED, BEFORE: Filtered_spectrum = Spectrum*inv_hp_tf
    
    
    #print("Filtered_spectrum:  ", len(Filtered_spectrum))
    
    
    
    
    Filtered_signal = scipy.ifft(Filtered_spectrum, n=M)  # Construct filtered signal , # CHANGED, BEFORE: Filtered_signal = scipy.ifft(Filtered_spectrum, n=M)
    plt.figure("Inv_Filtered_signal")
    plt.plot(Filtered_signal) 
    plt.show() 
    
    return Filtered_signal