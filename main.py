import os
import sys
import subprocess

script = None
run = True

base = os.path.dirname(__file__)

for arg in sys.argv[1:]:
	if arg == "-c":
		run = False
	else:
		if script == None:
			script = arg

if script == None:
	print("E: no script path provided")
	exit()

subprocess.run([sys.executable, os.path.join(base, "compile.py"), script])
if run:
	subprocess.run([sys.executable, os.path.join(base, "interpreter.py"), "out/compiled.stksc", "out/labels.txt"])