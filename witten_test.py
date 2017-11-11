import wittengram

if __name__ == "__main__":

	"""Program to train and test the fivegram model"""

	m = wittengram.Wittengram()
	m.train("english/train")
	m.start()
	
	correct = 0
	total = 0
	
	for line in open("english/dev"):
		for w in line.rstrip('\n'): 
			if m.predict() == w: #predict will return the most likely character in context
			# need likelihood of character rather than prediction
				correct += 1
			total += 1
			m.read(w) 
			#incorporate new data to model (necessary to keep track of grams)

	success = 100.0*float(correct/total)
	print("%{0} success".format(success)) #print success rate
