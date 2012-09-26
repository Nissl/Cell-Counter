# Just a little Matlab to CSV converter since I'm locked out of my Matlab 
# license.

# Tell the converter what you want it to do.
Mat_to_CSV = True
CSV_to_Mat = False # not implemented yet

# Where your files are located.
directory = r"C:\Documents and Settings\Administrator\My Documents\MAT Data"

# File name
filename = "AmygNissl"

# File type
filetype = "_neuron"

# Set of file numbers to convert
file_min = 1
file_max = 3

# Program here
import scipy.io
import csv

if Mat_to_CSV:
    for file_num in range(file_min, file_max + 1):
        try: 
            path = directory + "\\" + filename + str(file_num) + filetype 
            raw_import = scipy.io.loadmat(path, mdict=None, appendmat=True)
            out_path = path + ".txt"
            output_writer = csv.writer(open(out_path, 'w'), delimiter='\t',
                                       quotechar='|', 
                                       quoting=csv.QUOTE_MINIMAL)
            if filetype == "_whole":
                output_writer.writerow(["x1", "y1", "x2", "y2", "celltype"])
            else:
                output_writer.writerow(["x1", "y1", "x2", "y2"])
            for data_row in xrange(len(raw_import['cellexport'])):
                output_writer.writerow(raw_import['cellexport'][data_row])      
                
        except:
            print ("File " + filename + str(file_num) + 
                   filetype + " " + "not found")
  

#output_writer.writerow()
#        scipy.io.savemat(path, mdict={'cellexport': cellexport}, appendmat=True)