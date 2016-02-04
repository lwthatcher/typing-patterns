import numpy

class KDAnalyzer:

    def __init__(self,filename,time_interval_threshold):
        self.loadfile(filename,time_interval_threshold)
        return

    def loadfile(self,filename,time_interval_threshold):
        self.filename = filename
        self.time_interval_threshold = time_interval_threshold
        data = numpy.loadtxt(filename)
        self.data = data
        self.asciicodes = data[:,0].astype(numpy.int64)
        self.timestamps = data[:,1]

        # Building dictionary of key-strike pairs; ignoring pairs with interval greater
        # than 1 second
        pairs = dict()
        for i in xrange(0,len(self.asciicodes)-1):
            key = str(self.asciicodes[i])+':'+str(self.asciicodes[i+1])
            time_interval = numpy.abs(self.timestamps[i+1]-self.timestamps[i])
            if(time_interval < self.time_interval_threshold):
                if not(key in pairs):
                    pairs[key] = []
                pairs[key].append(time_interval)

        self.pairs = pairs
        return


# Loading data
print "Loading data..."

filename = "data/steven_gettysburg.txt"
time_interval_threshold = 1.0

print "File: ",filename

analyzer = KDAnalyzer(filename,time_interval_threshold)
asciicodes = analyzer.asciicodes
timestamps = analyzer.timestamps
pairs = analyzer.pairs


# Printing the pairs, but only if the count threshold is high enough.
count_threshold = 10
print "Pairs with count >= "+str(count_threshold)+":"
for pair in pairs:
    if( len(pairs[pair]) >= count_threshold):
        times_arr = numpy.array(pairs[pair])
        count = len(times_arr)
        average_time_interval = times_arr.sum()/count
        print "Pair: ",pair," Count: ",count," Average Time Interval: ",average_time_interval
