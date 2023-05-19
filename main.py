import os
import sys

path = None
run = True

for arg in sys.argv:
    if arg == "-c":
        run = False
    else:
        if path == None:
            path = arg