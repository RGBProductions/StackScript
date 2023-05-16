import os
import requests
import math

script = "memtest.stksc"
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

import random

class StackField:
	stacks = [[] for _ in range(256)]
	registers = {"s": 0, "v": 0, "c": 0, "r": random.randint(0,255)}
	callstack = []
	
	def push(stack,*vals):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		for val in vals:
			StackField.stacks[stack].append(val)
			StackField.registers["v"] = val
		StackField.registers["s"] = len(StackField.stacks[stack])
	
	def pop(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		for i in range(n):
			StackField.stacks[stack].pop()
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def clear(stack):
		stack -= 1
		if not (stack < 0 or stack >= len(StackField.stacks)):
			StackField.stacks[stack].clear()
		StackField.registers["s"] = 0
		StackField.registers["v"] = 0
	
	def clone(stack,n,stack2=None):
		stack -= 1
		if stack2 == None:
			stack2 = stack
		if stack2 < 0 or stack2 >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
		else:
			StackField.registers["s"] = len(StackField.stacks[stack])
			if StackField.registers["s"] > 0:
				StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
			else:
				StackField.registers["v"] = 0
			for i in range(n):
				StackField.stacks[stack2].append(StackField.registers["v"])
		StackField.registers["s"] = len(StackField.stacks[stack2])
	
	def move(stack1,stack2,n):
		stack1 -= 1
		stack2 -= 1
		pulled = []
		for i in range(n):
			pulled.append(StackField.stacks[stack1].pop())
		if stack2 < 0 or stack2 >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		for i in range(n):
			StackField.stacks[stack2].append(pulled.pop())
		StackField.registers["s"] = len(StackField.stacks[stack2])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack2][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def read(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def print(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			print("",end='')
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		s = ""
		StackField.registers["s"] = len(StackField.stacks[stack])
		for val in StackField.stacks[stack]:
			s += chr(val)
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
		print(s,end='')
	
	def println(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			print("")
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		s = ""
		StackField.registers["s"] = len(StackField.stacks[stack])
		for val in StackField.stacks[stack]:
			s += chr(val)
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
		print(s)
	
	def prntnum(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			print("",end='')
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
		print(StackField.registers["v"],end='')
	
	def prntraw(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			print("")
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		print(" ".join([str(i) for i in StackField.stacks[stack]]))
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def clrscr():
		os.system("clear")
	
	def input(stack):
		val = input()
		if val.isnumeric():
			StackField.push(stack,int(val))
		else:
			vals = []
			for i in range(len(val)):
				vals.append(ord(val[i]))
			StackField.push(stack,*vals)
	
	def cmp(val):
		StackField.registers["c"] = (StackField.registers["v"] > val)*1 - (StackField.registers["v"] < val)*1 + 0
	
	def cmpstk(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["s"] = 0
			val = 0
			StackField.registers["c"] = (StackField.registers["v"] > val)*1 - (StackField.registers["v"] < val)*1 + 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		val = StackField.stacks[stack][StackField.registers["s"]-1]
		StackField.registers["c"] = (StackField.registers["v"] > val)*1 - (StackField.registers["v"] < val)*1 + 0
	
	def jump(*args):
		if len(args) > 1: # Conditional
			if args[0] == "eq" and StackField.registers["c"] == 0:
				State.line = args[1]-2
			if args[0] == "ne" and StackField.registers["c"] != 0:
				State.line = args[1]-2
			if args[0] == "gr" and StackField.registers["c"] > 0:
				State.line = args[1]-2
			if args[0] == "ge" and StackField.registers["c"] >= 0:
				State.line = args[1]-2
			if args[0] == "ls" and StackField.registers["c"] < 0:
				State.line = args[1]-2
			if args[0] == "le" and StackField.registers["c"] <= 0:
				State.line = args[1]-2
		else:
			State.line = args[0]-2
	
	def call(*args):
		if len(args) > 1: # Conditional
			if args[0] == "eq" and StackField.registers["c"] == 0:
				StackField.callstack.append(State.line)
				State.line = args[1]-2
			if args[0] == "ne" and StackField.registers["c"] != 0:
				StackField.callstack.append(State.line)
				State.line = args[1]-2
			if args[0] == "gr" and StackField.registers["c"] > 0:
				StackField.callstack.append(State.line)
				State.line = args[1]-2
			if args[0] == "ge" and StackField.registers["c"] >= 0:
				StackField.callstack.append(State.line)
				State.line = args[1]-2
			if args[0] == "ls" and StackField.registers["c"] < 0:
				StackField.callstack.append(State.line)
				State.line = args[1]-2
			if args[0] == "le" and StackField.registers["c"] <= 0:
				StackField.callstack.append(State.line)
				State.line = args[1]-2
		else:
			StackField.callstack.append(State.line)
			State.line = args[0]-2
	
	def ret(*args):
		if len(args) > 1: # Conditional
			if args[0] == "eq" and StackField.registers["c"] == 0:
				State.line = StackField.callstack.pop()
			if args[0] == "ne" and StackField.registers["c"] != 0:
				State.line = StackField.callstack.pop()
			if args[0] == "gr" and StackField.registers["c"] > 0:
				State.line = StackField.callstack.pop()
			if args[0] == "ge" and StackField.registers["c"] >= 0:
				State.line = StackField.callstack.pop()
			if args[0] == "ls" and StackField.registers["c"] < 0:
				State.line = StackField.callstack.pop()
			if args[0] == "le" and StackField.registers["c"] <= 0:
				State.line = StackField.callstack.pop()
		else:
			State.line = StackField.callstack.pop()
	
	def inc(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.stacks[stack][StackField.registers["s"]-1] += 1
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def dec(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.stacks[stack][StackField.registers["s"]-1] -= 1
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def add(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		acc = StackField.stacks[stack].pop()
		for i in range(n-1):
			v = StackField.stacks[stack].pop()
			acc += v
		StackField.stacks[stack].append(acc)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def sub(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		acc = StackField.stacks[stack].pop()
		for i in range(n-1):
			acc -= StackField.stacks[stack].pop()
		StackField.stacks[stack].append(acc)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def mul(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		acc = StackField.stacks[stack].pop()
		for i in range(n-1):
			acc *= StackField.stacks[stack].pop()
		StackField.stacks[stack].append(acc)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def div(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		acc = StackField.stacks[stack].pop()
		for i in range(n-1):
			acc /= StackField.stacks[stack].pop()
		StackField.stacks[stack].append(acc)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def floor(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		StackField.stacks[stack][StackField.registers["s"]-1] = int(StackField.stacks[stack][StackField.registers["s"]-1])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def ceil(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.registers["s"] = len(StackField.stacks[stack])
		StackField.stacks[stack][StackField.registers["s"]-1] = math.ceil(StackField.stacks[stack][StackField.registers["s"]-1])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def inv(stack):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		StackField.stacks[stack].append(-StackField.stacks[stack].pop())
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def pull(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		itm = StackField.stacks[stack].pop(n-1)
		StackField.stacks[stack].append(itm)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def drop(stack,n):
		stack -= 1
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		itm = StackField.stacks[stack].pop()
		StackField.stacks[stack].insert(len(StackField.stacks[stack])-n,itm)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0
	
	def save(stack,name):
		stack -= 1
		spl = name.split("/")
		filename = spl[len(spl)-1] + ".bin"
		cur = "."
		for itm in spl[:-1]:
			cur = os.path.join(cur,itm)
			if not os.path.exists(cur):
				os.mkdir(cur)
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		with open(filename,"wb") as f:
			StackField.registers["v"] = 0
			for val in StackField.stacks[stack]:
				StackField.registers["v"] = val
				f.write(int(val).to_bytes(4, "little"))
			StackField.registers["s"] = len(StackField.stacks[stack])
	
	def load(stack,name):
		stack -= 1
		name += ".bin"
		if stack < 0 or stack >= len(StackField.stacks):
			StackField.registers["v"] = 0
			StackField.registers["s"] = 0
			return
		if not os.path.exists(name):
			StackField.registers["s"] = len(StackField.stacks[stack])
			if StackField.registers["s"] > 0:
				StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
			else:
				StackField.registers["v"] = 0
			return
		with open(name,"rb") as f:
			b = f.read(4)
			while b:
				print(b)
				StackField.push(stack, int.from_bytes(b, "little"))
				b = f.read(4)
		StackField.registers["s"] = len(StackField.stacks[stack])
		if StackField.registers["s"] > 0:
			StackField.registers["v"] = StackField.stacks[stack][StackField.registers["s"]-1]
		else:
			StackField.registers["v"] = 0

class State:
	line = 0
	gfxEnabled = False

class Inst:
	def run(*args):
		a = list(args)
		inst = a.pop(0).lower()
		for i,arg in enumerate(a):
			if arg.lstrip("-").isnumeric():
				a[i] = int(arg)
			if arg in StackField.registers:
				a[i] = StackField.registers[arg]
		StackField.__dict__[inst](*a)

def run(lines):
	while State.line < len(lines):
		args = lines[State.line].split()
		Inst.run(*args)
		State.line += 1
		StackField.registers["r"] = random.randint(0,255)

#with open(script) as f:
#	lines = f.read().splitlines()
#Precomp.compile(lines)
#if not os.path.exists("out"):
#	os.mkdir("out")
#with open("out/compiled.stksc", "w") as f:
#	f.write("\n".join(lines))
#run(lines)

while True:
	c = input("> ")
	if c == "exit":
		break
	args = c.split()
	Inst.run(*args)