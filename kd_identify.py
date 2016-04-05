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

# *** normal_pdf ***
# std: The standard deviation
# mean: The mean (average)
# x: The value at which to obtain the probability density
# Returns: The probability density
def normal_pdf(std,mean,x):
    return (1/(std*numpy.sqrt(2*numpy.pi))) * numpy.exp(-((x - mean)**2/(2*std**2)))


class KDIdentifier:

    # *** KDIdentifier init ***
    # id_names_files:  A dictionary, the each key is the known identity name, and each value
    #                  is a list of file paths of the data defining that identity.
    # time_interval_threshold: The maximum amount if time between keystrokes to be considered
    # freq_level: The minimum frequency of a key-pair event, before that set of events is considered.
    # history_length: The length of the history of events to rely on to compute the guess.
    # use_log_norm_pdf: Whether to take the norm pdf of original data or to take the norm pdf of log(data)
    def __init__(self,
                id_names_files,
                time_interval_threshold=1.2,
                freq_level=10,
                history_length=100,
                use_log_norm_pdf=False):

        self.id_names_files = id_names_files

        # Whether to take the norm pdf of original data
        # or to take the norm pdf of log(data)
        self.use_log_norm_pdf = use_log_norm_pdf

        # Assembling the learned identities
        self.known_ids = dict()
        for id in id_names_files:
            self.known_ids[id] = KDAnalyzer(self.id_names_files[id],
                                            time_interval_threshold=time_interval_threshold,
                                            freq_level=freq_level,
                                            id_name=id)

        # Create a list for each id candidate, to save the list of encountered probabilities
        self.probab_histories = dict()
        for id in id_names_files:
            self.probab_histories[id] = numpy.zeros(history_length).tolist()

        # Used to see if all the known ids have the desired key-pair
        self.success_bool = dict()
        for id in self.known_ids:
            self.success_bool[id] = False

        # Used to collect the probabilities from each known_id
        self.probs = dict()
        for id in self.known_ids:
            self.probs[id] = 0.0

        # Used to store the summation of all the probabilities so far, so we can get the maximum
        self.prob_sums = dict()
        for id in self.known_ids:
            self.prob_sums[id] = 0.0

        # Used to keep track of previous and current keystrokes.
        self.prev_ascii = -1
        self.prev_timestamp = -1.
        self.curr_ascii = -1
        self.curr_timestamp = -1.

        # The current guess
        self.guess = "<none>"


    # *** keypairtime_prob_density ***
    # pair: The tuple with the pair of ascii keys
    # time: the time that we want to find the probability density for.
    # known_id: The identity whose probabilities we want to check against.
    def keypairtime_prob_density(self,pair,time,known_id):
        success = False
        prob_dens = 0.0
        if( pair in known_id.freq_pairs ):
            if(self.use_log_norm_pdf):
                data = known_id.freq_pairs[pair]
                logdata = numpy.log(data)
                std_of_logdata = numpy.std(logdata)
                mean_of_logdata = numpy.mean(logdata)
                log_time = numpy.log(time)
                prob_dens = normal_pdf(std_of_logdata,mean_of_logdata,log_time)
                success = True
            else:
                std = numpy.std(known_id.freq_pairs[pair])
                mean = numpy.mean(known_id.freq_pairs[pair])
                prob_dens = normal_pdf(std,mean,time)
                success = True
        return success,prob_dens


    # *** processKeystroke ***
    # Processes a keystroke, and computes a new "guess" for the identity.
    # ascii_code: The ascii code of the key just pressed
    # timestamp:  The timestamp of the keypress.
    def processKeystroke(self,ascii_code,timestamp):
        self.curr_ascii = ascii_code
        self.curr_timestamp = timestamp
        if( self.prev_ascii >= 0 and self.prev_timestamp >= 0. ):
            pair = (self.prev_ascii,self.curr_ascii)
            time = self.curr_timestamp - self.prev_timestamp

            for id in self.known_ids:
                self.success_bool[id],self.probs[id] = self.keypairtime_prob_density(pair,time,self.known_ids[id])

            # we only use it if all of the ids had this pair
            success_all = True
            for id in self.known_ids:
                success_all = success_all and self.success_bool[id]

            if( success_all ):
                for id in self.known_ids:
                    # Append the newest probability, and remove the oldest one from the history.
                    self.probab_histories[id].remove(self.probab_histories[id][0])
                    self.probab_histories[id].append(self.probs[id])

                for id in self.known_ids:
                    self.prob_sums[id] = numpy.sum(numpy.array(self.probab_histories[id]))

                self.guess, max_prob = find_max(self.prob_sums)

        self.prev_ascii = self.curr_ascii
        self.prev_timestamp = self.curr_timestamp



if __name__ == "__main__":
    id_names_files = {"steven":["data/steven_gettysburg.txt","data/steven_gettysburg2.txt"],
                      "nozomu":["data/nozomu_gettysburg.txt"],
                      "lawrence":["data/lawrence_gettysburg.txt"],
                      "joseph":["data/joseph_gettysburg.txt"],
                      "wilson":["data/wilson_gettysburg.txt"]}

    inputfiles = ["data/wilson_obedience.txt",
                  "data/lawrence_emails.txt",
                  "data/steven2_gettysburg.txt",
                  "data/nozomu_obedience.txt",
                  "data/joseph_obedience.txt"]

    # Here, we simulate recieving data "live", as a person is typing,
    # by reading in the file top-to-bottom as if the person was typing it.

    # Open the input file
    inputdata = numpy.loadtxt(inputfiles[4])
    asciicodes = inputdata[:,0].astype(numpy.int64)
    timestamps = inputdata[:,1]

    kdidentifier = KDIdentifier(id_names_files,
                                history_length=100,
                                use_log_norm_pdf=True)

    # Now, iterate through each pair of letters, as if getting them from a live-stream
    for i in range(0,len(timestamps)):
        kdidentifier.processKeystroke(asciicodes[i],timestamps[i])
        print("Guess: ",kdidentifier.guess, " Probabs: ",kdidentifier.prob_sums)

    # Plotting one of the distributions with the data just to look at it.
    import matplotlib
    from matplotlib import pyplot
    matplotlib.interactive(True)
    test_analyzer = KDAnalyzer(id_names_files["steven"],
                                time_interval_threshold=1.2,
                                freq_level=10,
                                id_name=id)

    set = test_analyzer.freq_pairs[(32,119)]
    x = numpy.linspace(0+1e-12,numpy.max(set)+0.1,200)

    mean=numpy.mean(set)
    std=numpy.std(set)

    mean_oflogdata = numpy.mean(numpy.log(set))
    std_oflogdata = numpy.std(numpy.log(set))

    pyplot.figure()

    if(kdidentifier.use_log_norm_pdf):
        pyplot.plot(x,normal_pdf(std_oflogdata,mean_oflogdata,numpy.log(x)))
    else:
        pyplot.plot(x,normal_pdf(std,mean,x))

    pyplot.plot(set,numpy.zeros(len(set)),'*')
    pyplot.ylim([-0.5,3.0])
    pyplot.xlim([0,numpy.max(set)+0.1])
    pyplot.title("Example keystroke times with estimated normal")
