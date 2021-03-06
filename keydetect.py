#!/usr/bin/env python3

''' A keylogging gui for collecting typing data.
The logged information will be output to a file called "log.keys".

Usage:
    python3 keydetect.py [example.text]

example.text is the text that will be shown on the gui.  As the user types,
this program will compare what the user has typed with example.text and show
which characters the user typed correctly and which the user typed incorrectly.
Correctly typed characters will change color such that the background is black
and the letter becomes white; incorrectly typed characters will change color
such that the background is red (and the letter remains black).

Remember that this program is a keylogger.  Don't type anything you will regret
typing while this program is logging keys.
'''
import argparse
import sys
import tkinter as tk
import time
import pickle
from kd_identify import KDIdentifier
from typeroracle import TyperOracle
from hmm_oracle import HmmOracle

def set_textarea(textarea, showntext):
    ''' Sets text in text area '''
    textarea.config(state=tk.NORMAL)
    textarea.insert('1.0', showntext)
    textarea.config(state=tk.DISABLED)

def highlight_text(textarea, standardtext, typedsofar):
    ''' Highlights portions of text according to what has been typed by the user
    '''
    position = 0
    tag = 'correct'
    textarea.tag_remove('correct', '1.0', 'end')
    textarea.tag_remove('incorrect', '1.0', 'end')
    while position < len(typedsofar):
        start = position
        if typedsofar[position] == standardtext[position]:
            tag = 'correct'
            position += 1
            while (position < len(typedsofar)) and \
                    (typedsofar[position] == standardtext[position]):
                position += 1
        else:
            tag = 'incorrect'
            position += 1
            while (position < len(typedsofar)) and \
                    (typedsofar[position] != standardtext[position]):
                position += 1
        textarea.tag_add(tag, '1.0+%dc' % start, '1.0+%dc' % position)

def onkeypress(ofh, textarea, standardtext, typedsofar, kdidentifier, oracles):
    ''' Closure to handle modifying record of what user has typed '''
    def inner_onkeypress(event):
        ''' Callback function for when a character is typed '''
        # Python doesn't let us refer back to typedsofar passed into onkeypress
        # without the following line
        nonlocal typedsofar
        eventchar = event.char
        if eventchar == '\r':
            eventchar = '\n'
        if len(eventchar) > 0:
            t = time.time()
            ofh.write('%d %f\n' % (ord(eventchar), t))
            if ord(eventchar) == 8:  # if is a backspace
                typedsofar.pop()
            else:
                typedsofar += eventchar
            kdidentifier.processKeystroke(ord(eventchar), t)
            guess_i = kdidentifier.guess

            guess_str = "Guess: " + str(guess_i)
            for oracle in oracles:
                guess_o = oracle.process_keystroke(ord(eventchar), t)
                guess_str += " " + str(guess_o)
            print(guess_str)

        # sys.stdout.write(''.join(typedsofar)+'\n')
        highlight_text(textarea, standardtext, typedsofar)
    return inner_onkeypress

def build_textarea(rootwindow, showntext):
    ''' Creates text region.
    Also specifies tags for showing typed characters.  The tag types are:
        * correct - visual for correctly typed characters, with black background
        and white foreground
        * incorrect - visual for incorrectly typed characters, with red
        background and black foreground
    Characters that have not yet been typed should appear in the default white
    background and black foreground.
    '''
    textarea = tk.Text(
        rootwindow, background='white', foreground='black',
        font=('Monospace', 12), state=tk.DISABLED, wrap=tk.WORD)
    textarea.pack(fill='both')
    set_textarea(textarea, showntext)
    textarea.tag_configure('correct', background='black', foreground='white')
    textarea.tag_configure('incorrect', background='red', foreground='black')
    return textarea

def run_gui(showntext, _oracles_files=None):
    ''' Initializes global variables and starts gui '''
    standardtext = list(showntext)
    typedsofar = []

    id_names_files = {'lawrence': ['oracle/lawrence/lawrence_gettysburg2.txt',
                                   'oracle/lawrence/lawrence_obedience_partial.txt',
                                   'oracle/lawrence/lawrence_emails.txt',
                                   'oracle/lawrence/lawrence_proclamation_partial.txt',
                                   'oracle/lawrence/lawrence_gettysburg.txt',
                                   'oracle/lawrence/lawrence_obedience_partial2.txt',
                                   'oracle/lawrence/lawrence_decisiontrees.txt'],
                      'nozomu': ['oracle/nozomu/nozomu_gettysburg2.txt',
                                 'oracle/nozomu/nozomu_obedience.txt',
                                 'oracle/nozomu/nozomu_gettysburg.txt',
                                 'oracle/nozomu/nozomu_gettysburg3.txt'],
                      'jeff': ['oracle/jeff/jeff_gettysburg.txt',
                               'oracle/jeff/jeff_decisiontrees.txt',
                               'oracle/jeff/jeff_obedience.txt'],
                      'wilson': ['oracle/wilson/wilson_gettysburg3.txt',
                                 'oracle/wilson/wilson_gettysburg.txt',
                                 'oracle/wilson/wilson_gettysburg2.txt',
                                 'oracle/wilson/wilson_proclamation.txt',
                                 'oracle/wilson/wilson_obedience.txt'],
                      'steven': ['oracle/steven/steven_gettysburg3.txt',
                                 'oracle/steven/steven_gettysburg.txt',
                                 'oracle/steven/steven_gettysburg2.txt'],
                      'joseph': ['oracle/joseph/joseph_obedience.txt', 'oracle/joseph/joseph_gettysburg.txt']}

    kdidentifier = KDIdentifier(id_names_files,use_log_norm_pdf=True)
    oracle = None

    if _oracles_files is None:
        _oracles_files = []
    oracles = []
    for _o in _oracles_files:
        with open(_o, "rb") as ifh:
            oracle = pickle.load(ifh)
            oracles.append(oracle)
    rootwindow = tk.Tk()
    textarea = build_textarea(rootwindow, showntext)
    with open('log.keys', 'w') as ofh:
        rootwindow.bind('<Key>', onkeypress(
            ofh, textarea, standardtext, typedsofar, kdidentifier, oracles))
        rootwindow.mainloop()

def get_text_from_file(filename):
    ''' Extract text from file '''
    with open(filename) as ifh:
        result = ifh.read()
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', '-s',
                        default='docs/gettysburg.txt',
                        help='the source text file to use as input')
    parser.add_argument('--oracles', '-o',
                        nargs='*',
                        help='a list of the oracle files to use as oracles.')
    args = parser.parse_args()

    text = get_text_from_file(args.source)
    run_gui(text, args.oracles)

