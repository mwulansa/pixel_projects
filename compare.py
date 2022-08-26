file = open('file_timingscan.txt', 'r')
lines = file.readlines()

outfile = open('compare.txt', 'w')

outfile.writelines("""
	#!/bin/bash
	""")

for line in lines:
	if not line.strip() : continue
	if line:
		word = ' '.join(line.split())
		print word
		diff = "diff "+word+" ../../TriDAS_timingscan/pixel/"+word
		print diff
		outfile.writelines(
	diff+""" 
	echo """+diff.strip("diff")+"""\n""")