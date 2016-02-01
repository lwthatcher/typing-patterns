# Generates key loggin information
# Outputs to stdout
# Each line contains the ASCII code of the character typed, and the timestamp.
# Found how to do it here: http://stackoverflow.com/questions/17815686/detect-key-input-in-python

import sys
if( sys.version_info < (3,0)):
    import Tkinter as tk
else:
    import tkinter as tk
import time

def onKeyPress(event):
    c = event.char
    text.insert('end', '')
    #text.insert('end', '%s'%c)
    if(len(c)>0):
        sys.stdout.write('%d %f\n' % (ord(c),time.time()))
    #print("len(c):",len(c),"c:",c)

root = tk.Tk()
root.geometry('400x300')
text = tk.Text(root, background='black', foreground='white', font=('Comic Sans MS', 12))
text.pack()
root.bind('<KeyPress>', onKeyPress)
root.mainloop()
