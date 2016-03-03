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

datafiles = {"steven":"data/steven_gettysburg.txt",
             "nozomu":"data/nozomu_gettysburg.txt",
             "lawrence":"data/lawrence_gettysburg.txt"}

inputfiles = ["data/ethan_gettysburg.txt",
              "data/wilson_gettysburg.txt",
              "data/lawrence_emails.txt",
              "data/steven2_gettysburg.txt"]

learned_ids = []
for id in datafiles:
    learned_ids.append( KDAnalyzer(datafiles[id],time_interval_threshold=1.2,freq_level=10,id_name=id) )

