import os
import requests
import sys

if len(sys.argv) < 2:
	print("E: no script path provided")
	exit()

if not os.path.exists(sys.argv[1]):
	print("E: script path invalid")
	exit()

script = sys.argv[1]
if os.path.isdir(script):
	script += "/main.stksc"
subfolder = "."
spl = script.split("/")
if len(spl) > 1:
	subfolder = "/".join(spl[0:-1])

class Precomp:
	def compile(lines):
		ln = 0
		labels = {}
		while ln < len(lines):
			lines[ln] = lines[ln].lstrip(" ").lstrip("\t")
			line = lines[ln]
			if len(line) == 0:
				ln -= 1
				lines.remove(line)
				continue
			args = line.split()
			inst = args.pop(0)
			finalargs = [inst]
			isstr = False
			curstr = ""
			if inst.lower() == "netinc":
				restore = ln
				if not os.path.exists("netcache"):
					os.mkdir("netcache")
				spl = args[0].split("/")
				name = spl[len(spl)-1]
				if not os.path.exists(f"netcache/{name}"):
					response = requests.get(args[0])
					if response.status_code != 200:
						print(f"NETINC at line {ln+1} failed: {response.status_code}")
						exit()
					with open(f"netcache/{name}","w") as f:
						f.write(response.text)
				with open(f"netcache/{name}") as f:
					for ins in f.read().splitlines():
						lines.insert(ln,ins)
						ln += 1
				ln = restore
				ln -= 1
				lines.remove(line)
				continue
			if inst.lower() == "include":
				restore = ln
				with open(subfolder + "/" + args[0]) as f:
					for ins in f.read().splitlines():
						lines.insert(ln,ins)
						ln += 1
				ln = restore
				ln -= 1
				lines.remove(line)
				continue
			for i,arg in enumerate(args):
				if isstr:
					if arg.endswith('"'):
						curstr += arg[:-1]
						isstr = False
						for i in range(len(curstr)):
							finalargs.append(str(ord(curstr[i])))
						curstr = ""
					else:
						curstr += arg + " "
				else:
					if arg.startswith('"'):
						isstr = True
						if arg.endswith('"') and len(arg) > 1:
							curstr = arg[1:-1]
							isstr = False
							for i in range(len(curstr)):
								finalargs.append(str(ord(curstr[i])))
							curstr = ""
						else:
							curstr = arg[1:] + " "
					else:
						finalargs.append(arg)
			lines[ln] = " ".join(finalargs)
			ln += 1
		ln = 0
		while ln < len(lines):
			line = lines[ln]
			if len(line) == 0:
				ln -= 1
				lines.remove(line)
				continue
			args = line.split()
			if args[0].startswith(";"):
				ln -= 1
				lines.remove(line)
			if args[0].lower() == "label":
				labels[args[1]] = ln+1
				if len(args) > 2:
					labels[args[1]] = int(args[2])
				ln -= 1
				lines.remove(line)
			ln += 1
		for l,line in enumerate(lines):
			args = line.split()
			inst = args.pop(0)
			finalargs = [inst]
			for i,arg in enumerate(args):
				if arg in labels:
					args[i] = labels[arg]
				if arg.startswith(";"):
					break
				finalargs.append(str(args[i]))
			lines[l] = " ".join(finalargs)

with open(script) as f:
	lines = f.read().splitlines()
Precomp.compile(lines)
if not os.path.exists("out"):
	os.mkdir("out")
with open("out/compiled.stksc", "w") as f:
	f.write("\n".join(lines))