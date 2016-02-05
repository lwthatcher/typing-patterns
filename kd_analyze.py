import numpy

class ItoATools:
    non_char_chars = \
        {
            0	: "NUL",
            1	: "SOH",
            2	: "STX",
            3	: "ETX",
            4	: "EOT",
            5	: "ENQ",
            6	: "ACK",
            7	: "BEL",
            8	: "BS",
            9	: "HT",
            10	: "LF",
            11	: "VT",
            12	: "FF",
            13	: "CR",
            14	: "SO",
            15	: "SI",
            16	: "DLE",
            17	: "DC1",
            18	: "DC2",
            19	: "DC3",
            20	: "DC4",
            21	: "NAK",
            22	: "SYN",
            23	: "ETB",
            24	: "CAN",
            25	: "EM",
            26	: "SUB",
            27	: "ESC",
            28	: "FS",
            29	: "GS",
            30	: "RS",
            31	: "US",
            32	: "space",
            127	: "delete"
        }

    @classmethod
    def intToCharString(self,c_val):
        if( (c_val >= 0 and c_val <= 32) or c_val == 127 ):
            result = self.non_char_chars[c_val]
        else:
            result = str(chr(c_val))
        return result

    @classmethod
    def intTupleToCharTuple(self,thetuple):
        return '('+str(thetuple[0])+":"+self.intToCharString(thetuple[0])+','+str(thetuple[1])+":"+self.intToCharString(thetuple[1])+')'



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
        for i in range(0,len(self.asciicodes)-1):
            key = tuple((self.asciicodes[i],self.asciicodes[i+1]))
            time_interval = numpy.abs(self.timestamps[i+1]-self.timestamps[i])
            if(time_interval < self.time_interval_threshold):
                if not(key in pairs):
                    pairs[key] = []
                pairs[key].append(time_interval)

        self.pairs = pairs
        return


# Loading data
print("Loading data...")

filename = "data/steven_gettysburg.txt"
time_interval_threshold = 1.0

print("File: ",filename)

analyzer = KDAnalyzer(filename,time_interval_threshold)
asciicodes = analyzer.asciicodes
timestamps = analyzer.timestamps
pairs = analyzer.pairs


# Printing the pairs, but only if the count threshold is high enough.
count_threshold = 10
print("Pairs with count >= "+str(count_threshold)+":")
for pair in pairs:
    if( len(pairs[pair]) >= count_threshold ):
        times_arr = numpy.array(pairs[pair])
        count = len(times_arr)
        average_time_interval = times_arr.sum()/count
        print("Pair: ",ItoATools.intTupleToCharTuple(pair)," Count: ",count," Average Time Interval: ",average_time_interval)
