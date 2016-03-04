# Steven Schmidt
# kd_identify.py

"""
This is the idea:

(1) Read in known data files for identities {steven, lawrence, nozomu}.
(2) Get the name of the to-be-read-in input file that needs to be categorized.
(3) Initialize blank array of the probabilities of the 100 most recently detected key-pairs, one array for each identity
(4) Open the input file
(5) Read each key pair, one at a time. For each pair of key-strikes:
    (i) for each known identity {steven, lawrence, nozomu}:
        (a) find the probability of that time-distance-between-keystrikes
        (b) Put that probability at the front-end of the array for this identity, and pop off the one at the back-end of the array.
        (c) Sum the past 100 key-pairs' probabilities
            (FUTURE: with a linear weight that makes recent events more important than old events)
    (ii) Print the three probabilities to the screen, identifying the highest probability.
"""

from kd_analyze import KDAnalyzer
from kd_analyze import ItoATools
import numpy
import matplotlib
from matplotlib import pyplot
matplotlib.interactive(True)

# *** normal_pdf ***
# std: The standard deviation
# mean: The mean (average)
# x: The value at which to obtain the probability density
# Returns: The probability density
def normal_pdf(std,mean,x):
    return (1/(std*numpy.sqrt(2*numpy.pi))) * numpy.exp(-((x - mean)**2/(2*std**2)))

# *** keypairtime_prob_density ***
# pair: The tuple with the pair of ascii keys
# time: the time that we want to find the probability density for.
# known_id: The identity whose probabilities we want to check against.
def keypairtime_prob_density(pair,time,known_id):
    success = False
    prob_dens = 0.0
    if( pair in known_id.freq_pairs ):
        std = numpy.std(known_id.freq_pairs[pair])
        mean = numpy.mean(known_id.freq_pairs[pair])
        prob_dens = normal_pdf(std,mean,time)
        success = True
    return success,prob_dens
  
# *** find_max ***  
# Finds the maximum value in the dictionary, and the key of it.
# d: The dictionary
# Returns: key of maximum value, and maximum value.
def find_max(d):
    max_key = None
    max_val = numpy.finfo(0.0).min
    for key in d:
        if d[key] > max_val:
            max_key = key
            max_val = d[key]
    return max_key,max_val



id_names_files = {"steven":"data/steven_gettysburg.txt",
                  "nozomu":"data/nozomu_gettysburg.txt",
                  "lawrence":"data/lawrence_gettysburg.txt"}

inputfiles = ["data/ethan_gettysburg.txt",
              "data/wilson_gettysburg.txt",
              "data/lawrence_emails.txt",
              "data/steven2_gettysburg.txt"]

# Assembling the learned identities
known_ids = dict()
for id in id_names_files:
    known_ids[id] = KDAnalyzer(id_names_files[id],time_interval_threshold=1.2,freq_level=10,id_name=id)

# Plotting one of the distributions with the data just to look at it.
"""
set = known_ids["steven"].freq_pairs[(32,119)]
x = numpy.linspace(0,numpy.max(set)+0.1,200)
mean=numpy.mean(set)
std=numpy.std(set)
pyplot.figure()
pyplot.plot(x,normal_pdf(std,mean,x))
pyplot.plot(set,numpy.zeros(len(set)),'*')
pyplot.ylim([-0.5,3.0])
pyplot.xlim([0,numpy.max(set)+0.1])
"""

# Here, we simulate recieving data "live", as a person is typing,
# by reading in the file top-to-bottom as if the person was typing it.

# Open the input file
inputdata = numpy.loadtxt(inputfiles[1])
asciicodes = inputdata[:,0].astype(numpy.int64)
timestamps = inputdata[:,1]

# Create a list for each id candidate, to save the list of encountered probabilities
probab_lists = dict()
for id in id_names_files:
    probab_lists[id] = numpy.zeros(100).tolist()

# Now, iterate through each pair of letters, as if getting them from a live-stream
prev_ascii = -1
prev_timestamp = -1.
curr_ascii = -1
curr_timestamp = -1.

# Used to see if all the known ids have the desired key-pair
success_bool = dict()
for id in known_ids:
    success_bool[id] = False

# Used to collect the probabilities from each known_id
probs = dict()
for id in known_ids:
    probs[id] = 0.0

# Used to store the summation of all the probabilities so far, so we can get the maximum
prob_sums = dict()
for id in known_ids:
    prob_sums[id] = 0.0

for i in range(0,len(timestamps)):
    curr_ascii = asciicodes[i]
    curr_timestamp = timestamps[i]
    if( prev_ascii >= 0 and prev_timestamp >= 0. ):
        pair = (prev_ascii,curr_ascii)
        time = curr_timestamp - prev_timestamp
        for id in known_ids:
            success_bool[id],probs[id] = keypairtime_prob_density(pair,time,known_ids[id])
    
        # we only use it if all of the ids had this pair
        success_all = True
        for id in known_ids:
            success_all = success_all and success_bool[id]
            
        if( success_all ):
            for id in known_ids:
                probab_lists[id].remove(probab_lists[id][0])
                probab_lists[id].append(probs[id])
        
            output_str = ""
        
            for id in known_ids:
                prob_sums[id] = numpy.sum(numpy.array(probab_lists[id]))
                output_str += "{"+id+": "+str(prob_sums[id])+"}"
            
            max_id, max_prob = find_max(prob_sums)
            output_str += "  "+"Guess: "+max_id
            
            print(output_str)

    prev_ascii = curr_ascii
    prev_timestamp = curr_timestamp










