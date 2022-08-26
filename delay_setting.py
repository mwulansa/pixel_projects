
scanPoints = [14,13,12,9,6,3,2,1,0,-1,-2,-3,-6,-9,-12,-13,-14]
currentsetting = 1.5 #from the current globalDelay25 config defined with the Physics key
currentWBC = 164 #from dac defined with the Physics key

print("current delay setting:", currentsetting)
print("currentWBC:", currentWBC)

print("delay absolutePoint globalDelay25 globalDelay25(hex) wbc")

for delay in scanPoints:
	if delay >= 0:
		globaldelay25 = (delay + currentsetting)*2
		wbc = currentWBC
		print(delay, delay+currentsetting, globaldelay25, hex(int(globaldelay25)), wbc)
	else:
		if (delay + currentsetting)*2 < 0:
			globaldelay25 = (delay + currentsetting+25)*2
			wbc = currentWBC + 1
			print(delay, (delay+currentsetting)+25, globaldelay25, hex(int(globaldelay25)), wbc)
		else :
			globaldelay25 = (delay + currentsetting)*2
			wbc = currentWBC
			print(delay, (delay+currentsetting), globaldelay25, hex(int(globaldelay25)), wbc)

