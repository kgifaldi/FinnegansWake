#Kyle Gifaldi and John Nolan
#Multi-layer perceptron to identify languages in segments of the finnegans wake text
#based off the multi-mass softmax classification example

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, Activation
from keras.optimizers import SGD

def main():
	model = Sequential()
	#need to find number of letter types, n, and tag types, nt, n*t will be our vector size
	#we can cut out common letters, so I hope the result will be 50*20, close to 1000
	model.add(Embedding( 1000, 15, input_length=7))
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

	#Then we will have labes with 4 possible values (Joyce, Irish, French, German) 
	#An array of batchsize vectors, 1D with values ranging within 4. convert these:
	#one_hot_labels = keras.utils.to_categorical(labels, num_classes=4)

	#model.fit(data, one_hot_labels, epochs = 10, batch_size= ? )
	#prediction = model.predict(finnegans_clips, batch_size = ?, verbose=1) # should give us batch_size vectors of classifications,
	#so we print the parts it predicted as german. That's why it's key not to use RNN, or it might all be Joyce
	#go back through finnegans and print the segments that were tagged as german (and line number can be stored
	# with data, zip through it)
	#or do predict_on_batch for eatch line part of finnegans wake.

	#another great idea: shuffle training samples together, should train much better

if __name__=="__main__":
	main()
