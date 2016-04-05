import matplotlib
matplotlib.interactive(True)
from matplotlib import pyplot

from kd_analyze import KDAnalyzer
from kd_analyze import ItoATools
from kd_identify import *
import numpy


filenames = ["data/steven_gettysburg.txt",
             "data/nozomu_gettysburg.txt",
             "data/lawrence_gettysburg.txt",
             "data/wilson_gettysburg.txt",
             "data/lawrence_emails.txt",
             "data/steven2_gettysburg.txt"]

analyzer = KDAnalyzer([filenames[0]],time_interval_threshold=1.2,num_top_pairs=10,default_pairs="specific")


data = analyzer.freq_pairs[(100, 32)]

x = numpy.linspace(0,1.0,1000)
normpdf = normal_pdf(numpy.std(data),numpy.mean(data),x)
pyplot.figure()
pyplot.plot(x,normpdf)
pyplot.plot(data,numpy.zeros(len(data)),"*")
pyplot.title("data")


logdata = numpy.log(data)
minlogdata = numpy.min(logdata)
maxlogdata = numpy.max(logdata)
logdataspan = maxlogdata - minlogdata
x = numpy.linspace(minlogdata-logdataspan/2,maxlogdata+logdataspan/2,1000)
norm_of_log_data = normal_pdf(numpy.std(logdata),numpy.mean(logdata),x)
pyplot.figure()
pyplot.plot(x,norm_of_log_data)
pyplot.plot(logdata,numpy.zeros(len(logdata)),"*")
pyplot.title("log(data)")


# Original data
mindata = numpy.min(data)
maxdata = numpy.max(data)
dataspan = maxdata - mindata
x = numpy.linspace(mindata-dataspan/2,maxdata+dataspan/2,1000)

# Log of the data
norm_of_log_data_of_log_x = normal_pdf(numpy.std(numpy.log(data)),numpy.mean(numpy.log(data)),numpy.log(x))
pyplot.figure()
pyplot.plot(x,norm_of_log_data_of_log_x)
pyplot.plot(data,numpy.zeros(len(data)),"*")
pyplot.title("Normpdf(std_log_data,mean_log_data,log(x))")
