from kd_analyze import KDAnalyzer
from kd_analyze import ItoATools
from kd_identify import *
import typeroracle
import hmm_oracle
import numpy
np = numpy


# id_names_files: dictionary
# input_file: string
def test_permutation(id_names_files, input_file):

    # Open the input file
    inputdata = numpy.loadtxt(input_file)
    asciicodes = inputdata[:,0].astype(numpy.int64)
    timestamps = inputdata[:,1]

    kdidentifier = KDIdentifier(id_names_files,
                                history_length=200,
                                use_log_norm_pdf=True)
                                
    tyoracidentifier = typeroracle.build_typeroracle(id_names_files)
    
    hmmoracidentifier = hmm_oracle.build_typeroracle(id_names_files)

    # Now, iterate through each pair of letters, as if getting them from a live-stream
    for i in range(0,len(timestamps)):
        #print("flag,",i)
        kdidentifier.processKeystroke(asciicodes[i],timestamps[i])
        typeroracle_guess = tyoracidentifier.process_keystroke(asciicodes[i],timestamps[i])
        hmmoracle_guess = hmmoracidentifier.process_keystroke(asciicodes[i],timestamps[i])

    return {"log-norm": kdidentifier.guess,
            "typeroracle" : typeroracle_guess,
            "hhmoracle" : hmmoracle_guess}



id_names = ["joseph", "steven", "nozomu", "wilson", "lawrence", "jeff"]
file_base_names = ["gettysburg"]
file_postfixes = [".txt","2.txt","3.txt"]


for file_base in file_base_names:
    print("File: ",file_base)
    for leaveoutindex in range(0,3):
    
        print("Input index used for testing: ",leaveoutindex, " (others used for training)")
    
        # Construct the training data input, and test input file list
        id_names_files = dict()
        input_files = dict()
        for id in id_names:
            files_for_id = []
            input_file = ""
            for i,postfix in enumerate(file_postfixes):
                filename = "data/"+id+"_"+file_base+postfix
                if(i != leaveoutindex):   
                    files_for_id.append(filename)
                else:
                    input_file = filename
            id_names_files[id] = files_for_id
            input_files[id] = input_file

        # Now we do the testing
        for id in id_names:

            # Test on each test input.
            guess = test_permutation(id_names_files,input_files[id])
            print("Guess for '"+id+"': "+str(guess))

    


