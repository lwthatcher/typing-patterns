from kd_analyze import KDAnalyzer
from kd_analyze import ItoATools
from kd_identify import *
import numpy
np = numpy

id_names = ["steven","nozomu"]
file_base_names = ["gettysburg"]
file_postfixes = [".txt","2.txt","3.txt"]


# id_names_files: dictionary
# input_file: string
def test_permutation(id_names_files,input_file):

    # Open the input file
    inputdata = numpy.loadtxt(input_file)
    asciicodes = inputdata[:,0].astype(numpy.int64)
    timestamps = inputdata[:,1]

    kdidentifier = KDIdentifier(id_names_files,
                                history_length=100,
                                use_log_norm_pdf=True)

    # Now, iterate through each pair of letters, as if getting them from a live-stream
    for i in range(0,len(timestamps)):
        kdidentifier.processKeystroke(asciicodes[i],timestamps[i])
        #print("Guess: ",kdidentifier.guess, " Probabs: ",kdidentifier.prob_sums)

    return kdidentifier.guess


for leaveoutindex in range(0,3):

    # Construct the training data input, and test input file list
    id_names_files = dict()
    input_files = dict()
    for id in id_names:
        files_for_id = []
        input_file = ""
        for file_base in file_base_names:
            for i,postfix in enumerate(file_postfixes):
                filename = "data/"+id+"_"+file_base+postfix
                if(i != leaveoutindex):   
                    files_for_id.append(filename)
                else:
                    input_file = filename
        id_names_files[id] = files_for_id
        input_files[id] = input_file

    print("Leaving out index: ",leaveoutindex)

    # Test on each test input.
    for id in id_names:
        guess = test_permutation(id_names_files,input_files[id])
        print("Guess for '"+id+"': "+guess)

    


