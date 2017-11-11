import wittengram

if __name__ == "__main__":

	"""Program to train and test the fivegram model"""

	m = wittengram.Wittengram()
	m.train("english/train")
	m.start()
	
	for line in open("english/dev"):
		for w in line.rstrip('\n'): 
			m.prob(w) #gets the likelihood of following current set of characters
			m.read(w) 
			#incorporate new data to model (necessary to keep track of grams)
