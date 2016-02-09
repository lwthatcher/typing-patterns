import numpy
import matplotlib
matplotlib.interactive(True)
from matplotlib import pyplot

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
        return '('+self.intToCharString(thetuple[0])+','+self.intToCharString(thetuple[1])+')'

    @classmethod
    def intTupleToCharTupleLong(self,thetuple):
        return '('+str(thetuple[0])+":"+self.intToCharString(thetuple[0])+','+str(thetuple[1])+":"+self.intToCharString(thetuple[1])+')'


class KDAnalyzer:

    def __init__(self,filename,time_interval_threshold=1.0,num_top_pairs=10,default_pairs="all"):
        self.loadfile(filename,time_interval_threshold,num_top_pairs,default_pairs)
        return

    def loadfile(self,filename,time_interval_threshold,num_top_pairs,default_pairs):
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

        #Building "top_pairs":  The ten pairs most frequently encountered in the data
        top_pairs_list = []
        top_count = 0
        for pair in self.pairs:
            top_pairs_list.append((pair,self.pairs[pair]))
            if( len(top_pairs_list) > num_top_pairs ):
                #remove the item with the lowest count
                lowest_count = numpy.iinfo(numpy.int64).max
                found_index = 0
                for i in range(0,len(top_pairs_list)):
                    item = top_pairs_list[i]
                    if(len(item[1]) < lowest_count):
                        lowest_count = len(item[1])
                        found_index = i
                top_pairs_list.pop(found_index)

        self.top_pairs = dict(top_pairs_list)

        #Specific Pairs list
        specific_pairs_list = [(100,32), (114,32), (101,32), (116,104), (104,97), (114,101), (32,116), (104,101), (97,116), (116,32)]
        self.specific_pairs = dict()
        for pair in specific_pairs_list:
            self.specific_pairs[pair] = self.pairs[pair]

        if(default_pairs == "all"):
            self.default_pairs = self.pairs
        elif(default_pairs == "top"):
            self.default_pairs = self.top_pairs
        elif(default_pairs == "specific"):
            self.default_pairs = self.specific_pairs

        return

    def printPairs(self):
        pairs=self.default_pairs
        for pair in pairs:
            print(ItoATools.intTupleToCharTuple(pair)+": "+str(pairs[pair]))

    def printPairsSummary(self):
        # Printing the pairs, but only if the count threshold is high enough.
        pairs=self.default_pairs
        for pair in pairs:
            times_arr = numpy.array(pairs[pair])
            count = len(times_arr)
            average_time_interval = times_arr.sum()/count
            print("Pair: ",ItoATools.intTupleToCharTupleLong(pair),
                  " Count: ",count,
                  " Average Time Interval: ",average_time_interval,
                  " Min: ", numpy.min(pairs[pair]),
                  " Max: ", numpy.max(pairs[pair]),
                  " Standard Deviation: ",numpy.std(pairs[pair]))

    def plotBoxPlot(self):
        pairs=self.default_pairs
        data_to_plot = []
        xlabels = []
        for pair in pairs:
            data_to_plot.append(pairs[pair])
            xlabels.append(ItoATools.intTupleToCharTuple(pair))
        fig = pyplot.figure(figsize=(9, 6))
        ax = fig.add_subplot(111)
        bp = ax.boxplot(data_to_plot)
        pyplot.title(self.filename)
        ax.set_xticklabels(xlabels)
        pyplot.ylim((0,self.time_interval_threshold))


# Loading data
filenames = ["data/steven_gettysburg.txt",
            "data/nozomu_gettysburg.txt",
            "data/lawrence_gettysburg.txt"]

for filename in filenames:
    analyzer = KDAnalyzer(filename,time_interval_threshold=1.2,num_top_pairs=10,default_pairs="specific")
    analyzer.plotBoxPlot()
