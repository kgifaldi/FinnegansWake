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

german_files = ["langs/german/pg27769.txt"]

def main():
	model = Sequential()
	german = ""#"Ding an sich"#make_data()
	for file_name in german_files:
		with open(file_name) as gf:
			for line in gf:
				for c in line: 
					if c.isalpha():
						german += c + " " #forcing characterlevel hash
	#need to find number of letter types, n, and tag types, nt, n*t will be our vector size
	#we can cut out common letters, so I hope the result will be 50*20, close to 1000
	n = 100#how many letter_tag types we expect to see
	model.add(Embedding( n, 15, input_length=7))
	#model.add(Dropout(0.5)) #TODO: look into Dropout
	#model.add(Dense(7, activation='relu'))
	#model.add(Dropout(0.5))
	model.add(Dense(4, activation='softmax')) #4 classes

	#sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
	model.compile(loss='categorical_crossentropy',
			optimizer='adam', #sgd, #'rmsprop' might also work, or 'adam'
			metrics=['accuracy'])

	#then our data will be a set of vectors with the n*t range described above,
	#telling us the character and POS tag. (all special characters can be unk)
	# the vectors will be length 7, so shape will be batch_size, 7. 

	data = hashing_trick(german, n, hash_function='md5', lower=False, split=' ')
	for c, i in zip(german.split(' '), data):
		print(c, i) #just to show all characters are lined up with the hash
	#data = Tokenizer(n, lower=False, char_level=True).texts_to_matrix(german)
	#print(data)
	#with this data, will cut it into groups of 7 or whatever (this is just a list)
	# and also make a label for each of these groups with the german integer value

	#Then we will have labes with 4 possible values (Joyce, Irish, French, German) 
	#An array of batchsize vectors, 1D with values ranging within 4. convert these:
	#mix up labels in the same order as groups of characters
	#one_hot_labels = keras.utils.to_categorical(labels, num_classes=4)

	#model.fit(data, one_hot_labels, epochs = 10, batch_size= ? )
	#prediction = model.predict(finnegans_clips, batch_size = ?, verbose=1) # should give us batch_size vectors of classifications,
	#so we print the parts it predicted as german. That's why it's key not to use RNN, or it might all be Joyce
	#go back through finnegans and print the segments that were tagged as german (and line number can be stored
	# with data, zip through it)
	#or do predict_on_batch for eatch line part of finnegans wake.

	#another great idea: shuffle training samples together, should train much better

def make_data():
	#premake this stuff
	jar = '../stanford-postagger-full-2017-06-09/stanford-postagger.jar'
	model = '../stanford-postagger-full-2017-06-09/models/german-fast.tagger'
	german_tagger = StanfordPOSTagger(model, jar)
	german_with_tags = ""
	#can make this isomorphic with dictionary of data lists
	with open("german_data", "w+") as wf: #output all german data to a file
		for i, file_name in enumerate(german_files):
			with open(file_name) as gf:
				for j, line in enumerate(gf):
					text = german_tagger.tag(line.strip())
					"""
					for word, tag in text: #, tag in text:
						for c in word:
							wf.write("_".join([c, tag]) + " ")
					"""
					print(i, j)
	return german_with_tags

if __name__=="__main__":
	main()
#	make_data() #this takes very long, tagging each item
