#Kyle Gifaldi and John Nolan
#Multi-layer perceptron to identify languages in segments of the finnegans wake text
#based off the multi-mass softmax classification example

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, Activation
from keras.optimizers import SGD
from keras.preprocessing.text import hashing_trick, Tokenizer
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize
import numpy as np
import os

class FinnegansMLP:

	def __init__(self, n, i):
		"""Define letter vocab size, n, and input size, i"""

		self.n = n
		self.isize = i
		self.categories = ["french", "german", "irish", "joyce"]

	def compile_data(self, cat):
		"""Compile data for the given category (indexed in the following list)"""

		n = self.n
		i = self.isize

		text = ""
		for filename in os.listdir("./langs/" + self.categories[cat]):
			with open(filename) as tf:
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
			data.append(raw_data[i:i+isize])
			labels.append(cat) #an index for each category is training target
		
		#make into numpy arrays
		data = np.array(data)
		labels = np.array(labels)

		return np.array(data), np.array(labels)

	def run_model(self):
		model = Sequential()
		n = self.n#how many letter_tag types we expect to see
		isize= self.isize
		model.add(Embedding( n, 15, input_length=isize))
		#model.add(Dropout(0.5)) #TODO: look into Dropout
		#model.add(Dense(7, activation='relu'))
		#model.add(Dropout(0.5))
		model.add(Dense(4, activation='softmax')) #4 classes

		#sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
		model.compile(loss='categorical_crossentropy',
				optimizer='adam', #sgd, #'rmsprop' might also work, or 'adam'
				metrics=['accuracy'])
		data = np.array()
		labels = np.array()
		for i in range(4):
			idata, ilabels = self.compile_data(i)
			data.append(idata)
			
		one_hot_labels = keras.utils.to_categorical(labels, num_classes=4)

		model.fit(data, one_hot_labels, epochs = 10, batch_size=32)

		#prediction = model.predict(finnegans_clips, batch_size = 32, verbose=1) # should give us batch_size vectors of classifications,
		#so we print the parts it predicted as german. That's why it's key not to use RNN, or it might all be Joyce
		#go back through finnegans and print the segments that were tagged as german (and line number can be stored
		# with data, zip through it)
		#or do predict_on_batch for eatch line part of finnegans wake.

		#another great idea: shuffle training samples together, should train much better

	def make_data(self):
		"""generate the tagged data (which takes ages)"""

		jar = '../stanford-postagger-full-2017-06-09/stanford-postagger.jar'
		german_model = '../stanford-postagger-full-2017-06-09/models/german-fast.tagger'
		german_tagger = StanfordPOSTagger(german_model, jar)

		with open("german_data", "w+") as wf: #output all german data to a file
			for filename in os.listdir("./langs/german"):
				with open("./langs/german/" + filename) as gf:
					for line in gf:
						text = german_tagger.tag(line.strip())
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
				with open("./langs/french/" + filename) as ff:
					for line in ff:
						text = french_tagger.tag(line.strip())
						for word, tag in text: #, tag in text:
							for c in word:
								wf.write("_".join([c, tag]) + " ")
							wf.write("_" + " ") #space character
						if text:
							wf.write("\n")
		
		english_model = '../stanford-postagger-full-2017-06-09/models/english-left3words-distsim.tagger'
		english_tagger = StanfordPOSTagger(english_model, jar)
		with open("finnegans_data", "w+") as wf:
			with open("./langs/finnegans.txt") as fif:
				for line in fif:
					text = english_tagger.tag(line.strip())
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
	fmodel = FinnegansMLP(100, 9) #vocab size and input length
	fmodel.make_data() #this takes very long, tagging each item
