def convert_to_matrix_file(fname = None, path = None):
    
    if fname is None or path is None:
        raise Exception("File name and path must be passed!")

    import numpy as np

    def isfloat(value):
        try:
            float(value)
            return True
        except:
            return False


    file_name = fname
    
    file_path = path 

    full_name = file_path + "/" + file_name
    
    mat = []

    f = open(full_name,"r") # Open file
    lines = f.readlines()  # Read file
    
    iv_count = [0]
    iv_num = 0
    
        
    tmp = open('tmp.txt','w')  #  Open temp file
    
    for i,line in enumerate(lines[:len(lines)-1]):  # Skip the last ugly row
        if isfloat(line[:3]):
            tmp.write(line)  # Fill the buffer file skipping unneccesarry lines
            iv_count[iv_num] += 1 
        elif i > 30 and line == "\n":  # Splitting separate IV traces
            iv_count.append(0)
            iv_num += 1 
            
    
                
    tmp.close()
    
    mat = np.loadtxt('tmp.txt')
    
    new_mat = np.zeros((iv_count[0], len(iv_count)))
        
    left_of = 0
    
    for col,iv in enumerate(iv_count[:(len(iv_count)-1)]):
        new_mat[:,col] = mat[left_of:iv+left_of,2]

        left_of += iv
        
    
    np.savetxt(fname=full_name + "_matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')    
    
    
    
    
    
    
                
            


