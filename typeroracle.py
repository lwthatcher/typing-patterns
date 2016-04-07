"""
Attempt at classification via KDE voting

Build KDEs from key-pair timing information, then use majority vote for
classification.
"""
import random
import argparse
import numpy as np
import os
import pickle
from sklearn.neighbors import KernelDensity
import sys

HISTORY_LENGTH = 200

class TyperOracle:
    """
    A struct to store information for predicting typer
    """

    def __init__(self, keypairlist, userlist, labeledkdes):
        """
         * keypairlist must be a list of key-pair tuples
         * userlist must be a list of labels
         * labeledkdes must be a dictionary of label: {keypair: kde}
        """
        self.keypairlist = keypairlist
        self.userlist = userlist
        self.labeledkdes = labeledkdes
        self.history = []
        self.currentdata = {}
        self.last_timestamp = -1
        self.last_keypress = -1

    def predict(self, data):
        """
        for predicting in batch, when typing data is given offline
         * data must be a dictionary of keypair: [timings]
        returns the label that seems to best fit the data
        """
        votes = []
        for k in self.keypairlist:
            if k in data and len(data[k]) > 0:
                bestscore = float("-inf")
                bestlabel = -1
                for i in range(len(self.userlist)):
                    curscore = self.labeledkdes[self.userlist[i]][k].score(
                        np.reshape(data[k], (len(data[k]), 1)))
                    if curscore > bestscore:
                        bestscore = curscore
                        bestlabel = i
                if bestlabel >= 0:
                    votes.append(bestlabel)
        if votes:
            return self.userlist[np.argmax(np.bincount(votes))]
        return random.randint(0, len(self.userlist))

    def process_keystroke(self, ascii_code, timestamp):
        """
        for predicting live
         * ascii_code is an integer code for the latest key press
         * timestamp is a float of the timestamp for the key press
        """
        if len(self.history) == 0 and self.last_keypress == -1:
            self.last_keypress = ascii_code
            self.last_timestamp = timestamp
            return "I don't know"
        self.history.append((self.last_keypress, ascii_code))
        self.last_keypress = ascii_code
        self._update_currentdata(timestamp)
        self.last_timestamp = timestamp
        return self.predict(self.currentdata)

    def _update_currentdata(self, timestamp):
        """
        this method really shouldn't every be called outside of the class, since
        this method will change the state of the class
         * timestamp is a float of the timestamp for the latest key press
        """
        if self.history[-1] not in self.currentdata:
            self.currentdata[self.history[-1]] = []
        self.currentdata[self.history[-1]].append(timestamp - self.last_timestamp)
        if len(self.history) > HISTORY_LENGTH:
            if len(self.currentdata[self.history[0]]) == 1:
                self.currentdata.pop(self.history[0])
            else:
                self.currentdata[self.history[0]].pop(0)
            self.history = self.history[-HISTORY_LENGTH:]

def build_typeroracle(training):
    """
     * training is a dictionary of label: [training files]

    returns a TyperOracle
    """
    userlist = [label for label in training]
    labeledtimelists = _get_training_data(training, userlist)
    notinall = _get_limited_keypairs(userlist, labeledtimelists)
    prekeypairlist = _get_legal_keypairs(labeledtimelists, notinall)
    # TODO if there are too many KDEs, prune by choosing best N
    keypairlist = prekeypairlist
    labeledkdes = _build_labeledkdes(keypairlist, userlist, labeledtimelists)
    return TyperOracle(keypairlist, userlist, labeledkdes)

def _load_data(filename):
    """
    extracts key-pair information and the time elapsed between the first key
    press and the second key press of each key-pair
     * filename is the name of a file from which to load data; each line should
       contain <integer><whitespace><float>, where the integer is an ascii key
       code and the float is the timestamp when the key was pressed

    returns dictionary of keypair: [timings]
    """
    rawdata = np.loadtxt(filename)
    asciicodes = rawdata[:, 0].astype(np.int64)
    timestamps = rawdata[:, 1]

    keypair = [(a, b) for a, b in zip(asciicodes[:-1], asciicodes[1:])]
    timings = np.diff(timestamps)

    result = {}
    for k, time in zip(keypair, timings):
        if k in result:
            result[k].append(time)
        else:
            result[k] = [time]
    return result

def _get_training_data(training, userlist):
    """
     * training is a dictionary of label: [training files]
     * userlist is a list of users

    returns a dictionary of label: {keypair: [timing]}
    """
    labeledtimelists = {}
    for label in userlist:
        for filename in training[label]:
            data = _load_data(filename)
            if label not in labeledtimelists:
                labeledtimelists[label] = {}
            for keypair in data:
                if keypair not in labeledtimelists[label]:
                    labeledtimelists[label][keypair] = []
                labeledtimelists[label][keypair].extend(data[keypair])
    return labeledtimelists

def _get_limited_keypairs(userlist, labeledtimelists):
    """
    limited, as an antonym of universal: so this function grabs those key-pairs
    not present in every user"s data
     * userlist is a list of users
     * labeledtimelists is a dictionary of label: {keypair: [timing]}

    returns a dictionary of keypair: True
    """
    notinall = {}
    for i in range(len(userlist)):
        for j in range(i+1, len(userlist)):
            for keypair in labeledtimelists[userlist[i]]:
                if keypair not in labeledtimelists[userlist[j]]:
                    notinall[keypair] = True
    return notinall

def _get_legal_keypairs(labeledtimelists, notinall):
    """
     * labeledtimelists is a dictionary of label: {keypair: [timing]}
     * notinall denotes which key-pairs are not legal; it is a dictionary of
       keypair: True

    returns list of legal key-pairs
    """
    legal = []
    for _, keypairs in labeledtimelists.items():
        for keypair in keypairs:
            if keypair not in notinall:
                legal.append(keypair)
        # we actually need only the first data set to determine what the legal
        # key-pairs are
        break
    return legal

def _build_labeledkdes(keypairlist, userlist, labeledtimelists):
    """
     * labeledtimelists is a dictionary of label: {keypair: [timing]}
     * userlist is a list of users
     * labeledtimelists is a dictionary of label: {keypair: [timing]}

    returns a dictionary of label: {keypair: kde}
    """
    labeledkdes = {}
    for user in userlist:
        labeledkdes[user] = {}
        for keypair in keypairlist:
            timings = labeledtimelists[user][keypair]
            kde = KernelDensity()
            kde.fit(np.reshape(timings, (len(timings), 1)))
            labeledkdes[user][keypair] = kde
    return labeledkdes

def _kde_kl(kde_p, kde_q, n_samples=10**5):
    """
     * kde_p is a trained instance of sklearn.neighbors.KernelDensity
     * kde_q is a trained instance of sklearn.neighbors.KernelDensity
     * n_samples is the number of samples to take in making the calculation

    returns an estimate of KL(kde_p || kde_q), the KL divergence

    inspired by
    http://stackoverflow.com/questions/26079881/kl-divergence-of-two-gmms
    """
    samples = kde_p.sample(n_samples)
    log_p_samples, _ = kde_p.score_samples(samples)
    log_q_samples, _ = kde_q.score_samples(samples)
    return log_p_samples.mean() - log_q_samples.mean()

def _train_model(args):
    """
    runs training task
    """
    training = {}
    for dirname in os.listdir(args.dir):
        curdir = os.path.join(args.dir, dirname)
        training[dirname] = [os.path.join(
            curdir, a) for a in os.listdir(curdir)]
    oracle = build_typeroracle(training)
    with open(args.out, "wb") as ofh:
        pickle.dump(oracle, ofh)

def _predict_user(args):
    """
    runs prediction task
    """
    data = _load_data(args.input)
    with open(args.model, "rb") as ifh:
        oracle = pickle.load(ifh)
    print(oracle.predict(data))

def _run():
    """
    parses arguments and runs appropriate task
    """
    parser = argparse.ArgumentParser(
        description="A program for identifying typers.")
    subparsers = parser.add_subparsers()

    trainparser = subparsers.add_parser("train", help="train model")
    trainparser.add_argument(
        "dir",
        help="directory where training data are found; within dir should "
        "be subdirectories, each named by label, and each subdirectory "
        "should contain the training files, where each line contains "
        "<integer><whitespace><float>, where the integer represents an "
        "ascii key code and its corresponding float is the timestamp "
        "for when the key was pressed")
    trainparser.add_argument(
        "out",
        help="name of output file in which trained model is saved")
    trainparser.set_defaults(func=_train_model)

    predictparser = subparsers.add_parser("predict", help="predict typer")
    predictparser.add_argument(
        "model",
        help="name of file containing trained model")
    predictparser.add_argument(
        "input",
        help="name of file where each line contains "
        "<integer><whitespace><float>, where the integer reprsents an ascii "
        "key code and its corresponding float is the timestamp for when the "
        "key was pressed")
    predictparser.set_defaults(func=_predict_user)

    args = parser.parse_args()
    if "func" not in args:
        # bug in argparse throws very unhelpful message when task is not
        # specified
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    _run()

