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
import sys
import tkinter as tk
import time
import pickle
from kd_identify import KDIdentifier
from typeroracle import TyperOracle

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

def onkeypress(ofh, textarea, standardtext, typedsofar, kdidentifier, oracle):
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
            if oracle is not None:
                guess_o = oracle.process_keystroke(ord(eventchar), t)
                print("Guess: ", guess_i, guess_o)
            else:
                print("Guess: ", guess_i)

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

def run_gui(showntext, oracle_file=None):
    ''' Initializes global variables and starts gui '''
    standardtext = list(showntext)
    typedsofar = []

    id_names_files = {"steven":"data/steven_gettysburg.txt",
                      "nozomu":"data/nozomu_gettysburg.txt",
                      "lawrence":"data/lawrence_gettysburg.txt"}

    kdidentifier = KDIdentifier(id_names_files)
    oracle = None
    if oracle_file is not None:
        with open(oracle_file, "rb") as ifh:
            oracle = pickle.load(ifh)

    rootwindow = tk.Tk()
    textarea = build_textarea(rootwindow, showntext)
    with open('log.keys', 'w') as ofh:
        rootwindow.bind('<Key>', onkeypress(
            ofh, textarea, standardtext, typedsofar, kdidentifier, oracle))
        rootwindow.mainloop()

def get_text_from_file(filename):
    ''' Extract text from file '''
    with open(filename) as ifh:
        result = ifh.read()
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stdout.write('No text to show\n')
        sys.exit(0)
    if len(sys.argv) < 3:
        sys.stdout.write('No oracle to use\n')
        run_gui(get_text_from_file(sys.argv[1]))
    run_gui(get_text_from_file(sys.argv[1]), sys.argv[2])

