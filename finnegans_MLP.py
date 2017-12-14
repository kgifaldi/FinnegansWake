#Kyle Gifaldi and John Nolan
#Multi-layer perceptron to identify languages in segments of the finnegans wake text
#based off the multi-mass softmax classification example

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, Activation, Flatten
from keras.optimizers import SGD
from keras.preprocessing.text import hashing_trick, Tokenizer
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize
import numpy as np
import os
import re

class FinnegansMLP:

	def __init__(self, n, i, t):
		"""Define letter vocab size, n, and input size, i"""

		self.n = n
		self.isize = i
		self.categories = ["french", "german", "irish", "joyce"]
		self.tagging = t

	def compile_tag_data(self, cat):
		"""Compile data for the given category (indexed in the following list)"""

		n = self.n
		isize = self.isize
		
		if cat == 2:
			return [], [] # no irish data

		text = ""
		with open(self.categories[cat] + "_data") as tf:
			for line in tf:
				text += line.strip() #setup for character level hashing

		raw_data = hashing_trick(text, n, hash_function='md5', lower=False, split=' ')

		#with this data, will cut it into groups of isize (this is just a list)
		# and also make a label for each of these groups with the category index 
		labels = []
		data = []
		for i in range(0, len(raw_data), isize):
			if i + isize < len(raw_data): #in bounds
				data.append(raw_data[i:i+isize])
			else:
				zeros = [0]*(i+isize - len(raw_data)) #pad the rest of the values
				data.append(raw_data[i:len(raw_data)] + zeros)
			labels.append(cat) #an index for each category is training target
		return data, labels #return two arrays 


	def compile_data(self, cat):
		"""Compile data for the given category (indexed in the following list)"""

		n = self.n
		isize = self.isize

		text = ""
		for filename in os.listdir("./langs/" + self.categories[cat]):
			with open("./langs/" + self.categories[cat] + "/" + filename) as tf:
				for line in tf:
					for c in line:
						if c.isalpha():
							text += c + " " #setup for character level hashing
						elif c == " ":
							text += "_ "

		raw_data = hashing_trick(text, n, hash_function='md5', lower=False, split=' ')

		#with this data, will cut it into groups of isize (this is just a list)
		# and also make a label for each of these groups with the category index 
		labels = []
		data = []
		for i in range(0, len(raw_data), isize):
			if i + isize < len(raw_data): #in bounds
				data.append(raw_data[i:i+isize])
			else:
				zeros = [0]*(i+isize - len(raw_data)) #pad the rest of the values
				data.append(raw_data[i:len(raw_data)] + zeros)
			labels.append(cat) #an index for each category is training target
		return data, labels #return two arrays 

	def make_test_data(self, line):
		"""Make data set to predict the languages in a line of finnegans wake."""
		line = line.strip()
		text = ""
		for c in line:
			if c == " ":
				text += "_ " #encode spaces just like test data
			else:
				text += c + " "
		
		raw_data = hashing_trick(text, self.n, hash_function='md5', lower=False, split=' ')

		data = []
		if len(raw_data) < self.isize: #add padding
			data.append(raw_data + [0]*(self.isize-len(raw_data))) #add 0 up to isize
		for i in range(len(raw_data)-self.isize): #get every isize length window
			data.append(raw_data[i:i+self.isize]) #get encodings for this window
		return data
		
	def run_model(self):
		model = Sequential()
		n = self.n#how many letter_tag types we expect to see
		isize= self.isize

		model.add(Embedding(n, 15, input_length=isize))

		model.add(Flatten())

		model.add(Dense(4, activation='softmax')) #4 classes, TODO: consider sigmoid, could be more generous

		#sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
		model.compile(loss='categorical_crossentropy',
				optimizer='adam', #sgd, #'rmsprop' might also work
				metrics=['accuracy'])
		data = []
		labels = [] #concatenate all data and labels
		for i in range(4):
			if self.tagging:
				idata, ilabels = self.compile_tag_data(i)
			else:
				idata, ilabels = self.compile_data(i)
			data += idata
			labels += ilabels

		perm = np.random.permutation(len(data)) #shuffle data and labels
		data = np.array([np.array(data[i]) for i in perm])
		labels = np.array([labels[i] for i in perm])
			
		one_hot_labels = keras.utils.to_categorical(labels, num_classes=4)

		model.fit(data, one_hot_labels, epochs=20, batch_size=32)

		if self.tagging:
			suffix = "_NNT"
		else:
			suffix = "_NN"

		with open("output/french" + suffix, "w+") as of, open("output/german" + suffix, "w+") as og, open("output/irish" + suffix, "w+") as oi:
			if self.tagging:
				testdata = "finnegans_data"
			else:
				testdata = "langs/finnegans.txt"
			for line in open(testdata):
				f = False #have found these in the line
				g = False
				ir = False
				lastf = -1000 #last index where this language appeared (should be somewhat far apart)
				lastg = -1000
				lastir = -1000
				integer_samples = self.make_test_data(line)
				if len(line) < self.isize:
					continue #too short to consider
				if not integer_samples:
					continue #sometimes will be an empty line
				samples = np.array([np.array(s) for s in integer_samples])
				prediction = model.predict(samples, batch_size=len(integer_samples), verbose=1) # should give us batch_size vectors of classifications,
				for i, v in enumerate(prediction): #should be a prediction for each index in line
					line = line.strip()
					if self.tagging: #remove part of speech tags
						line = re.sub('_[^ ]+ ', '', line)
						line = re.sub('_', '', line) #remove space subsitutes

					best = np.argmax(v) #this gives us the best language for that part
					#Perhaps we could add everything that's better than the joyce tag. That's a good strategy

					if i + self.isize > len(line): #clip bounds
						r = len(line)
					else:
						r = i + self.isize

					if best == 0:
						if not f: #first french word found, write line
							of.write(line + "\n")
							f = True
						if i - lastf > self.isize and r - i > 2:
							of.write(line[i:r] + "\n")
							lastf = i #reset index
					if best == 1:
						if not g: 
							og.write(line + "\n")
							g = True
						if i - lastg > self.isize and r - i > 2:
							og.write(line[i:r] + "\n")
							lastg = i	
					if best == 2:
						if not ir:
							oi.write(line + "\n")
							ir = True
						if i - lastir > self.isize and r - i > 2:
							oi.write(line[i:r] + "\n") #picked this part of the line
							lastir = i
				if f:
					of.write("\n") #begin new line if we wrote to the output files
				if g:
					og.write("\n")
				if ir:
					oi.write("\n")

		#so we print the parts it predicted for each language. That's why it's key not to use RNN, or it might all be Joyce
		#we are predicting languages for each small window on the text.

	def make_tag_data(self):
		"""generate the tagged data (which takes ages)"""

		jar = '../stanford-postagger-full-2017-06-09/stanford-postagger.jar'
		german_model = '../stanford-postagger-full-2017-06-09/models/german-fast.tagger'
		german_tagger = StanfordPOSTagger(german_model, jar)

		with open("german_data", "w+") as wf: #output all german data to a file
			for filename in os.listdir("./langs/german"):
				print(filename + "...")
				with open("./langs/german/" + filename) as gf:
					for line in gf:
						print(line.strip())
						text = german_tagger.tag(word_tokenize(line.strip()))
						for word, tag in text: #, tag in text:
							for c in word:
								wf.write("_".join([c, tag]) + " ")
							wf.write("_" + " ") #space character
						if text:
							wf.write("\n")

		english_model = '../stanford-postagger-full-2017-06-09/models/english-left3words-distsim.tagger'
		english_tagger = StanfordPOSTagger(english_model, jar)

		print("finnegans wake...")
		with open("finnegans_data", "w+") as wf:
			with open("./langs/finnegans.txt") as fif:
				for line in fif:
					print(line.strip())
					text = english_tagger.tag(word_tokenize(line.strip()))
					for word, tag in text: #, tag in text:
						for c in word:
							wf.write("_".join([c, tag]) + " ")
						wf.write("_" + " ") #space character
					if text:
						wf.write("\n")

		with open("joyce_data", "w+") as wf: #output all joyce data to a file
			for filename in os.listdir("./langs/joyce"):
				print(filename + "...")
				with open("./langs/joyce/" + filename) as ff:
					for line in ff:
						print(line.strip())
						text = english_tagger.tag(word_tokenize(line.strip()))
						for word, tag in text: #, tag in text:
							for c in word:
								wf.write("_".join([c, tag]) + " ")
							wf.write("_" + " ") #space character
						if text:
							wf.write("\n")
		
		french_model = '../stanford-postagger-full-2017-06-09/models/french.tagger'
		french_tagger = StanfordPOSTagger(french_model, jar)
		with open("french_data", "w+") as wf: #output all french data to a file
			for filename in os.listdir("./langs/french"):
				print(filename + "...")
				with open("./langs/french/" + filename) as ff:
					for line in ff:
						print(line.strip())
						text = french_tagger.tag(word_tokenize(line.strip()))
						for word, tag in text: #, tag in text:
							for c in word:
								wf.write("_".join([c, tag]) + " ")
							wf.write("_" + " ") #space character
						if text:
							wf.write("\n")
		#Then we will have labes with 4 possible values (Joyce, Irish, French, German) 
		#An array of batchsize vectors, 1D with values ranging within 4. convert these:
		#mix up labels in the same order as groups of characters

		#our data could be a set of vectors with the n*t range described above,
		#telling us the character and POS tag. (all special characters can be unk)
		# the vectors will be length 'isize', so shape will be batch_size, isize. 
		# see make_data for pos tagging


if __name__=="__main__":
	fmodel = FinnegansMLP(100, 9, False) #vocab size and input length, tagging using tagging or not
	#fmodel.make_tag_data() #this takes very long, tagging each item
	fmodel.run_model()
