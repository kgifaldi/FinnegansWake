import collections

class Wittengram(object):
    """Five gram model with witten-bell smoothing"""

    def __init__(self, n):
        self.gram_counts = {} #dictionary of counts for the 4-grams (or less), size of each counter collection tells us the type
        self.total_counts = collections.Counter() #counts for each gram
        self.counts = collections.Counter() # count of each individual character
        self.total = 0 #total characters seen (NOTE: changed to 1 for keyboard)
        self.n = n #ngram model

    def train(self, filename):
        """Train the model on a text file."""
        self.s = "" #initialize string, this is not self.s used in reading, just for training
        for line in open(filename):
            for w in line.rstrip('\n'):
                self.read_and_train(w)
        self.s = "" #reset, as we are done with training
 

    def start(self):
        """Reset the state to the initial state."""
        self.s = "" # gram string is blank again

    def predict(self): # predict the most likely character following the current string s #need to use probabilities now
        last = self.s[-1:] #last character in latest rolling string
        best = "t" #no real guess at first
        max_p = 0.0
        for w in list(self.gram_counts[last]): #test the unique items following last two letters
            prob = self.prob(w)
            if prob > max_p:
                max_p = prob
                best = w
        return best #return best guess
                
    def read(self, w):
        """Read in character w, updating the state."""
        self.s += w #add new character to rolling gram string
        if len(self.s) > self.n: 
            self.s = self.s[1:] #chop off first character if past gram limit, n

    def read_and_train(self, w):
        """Read in character and update counts."""
        self.setw(w, self.s)
        self.counts[w] += 1
        self.total += 1
        self.read(w)

    def setw(self, w, s):
        """Set all the dictionaries to record this word with this sequence"""
        if s in self.gram_counts:
            self.gram_counts[s][w] += 1
            self.total_counts[s] += 1
        else: # have not seen this sequence
            self.gram_counts[s] = collections.Counter() #start counter for s*
            self.gram_counts[s][w] += 1
            self.total_counts[s] += 1
        if (len(s) > 1):
            self.setw(w, s[1:]) #continue on with next subset
   
    def smoothing(self, w, u):
        """Recursive function to calculate the additive smoothing"""
        if len(u) == 0:
            return self.counts[w]/self.total #return probability of w occurring at all (will have seen each letter)
        if u in self.total_counts:
            lambd = float(self.total_counts[u]/float(self.total_counts[u] + len(list(self.gram_counts[u])))) #value of lambda function
            #len of gram_counts[u] as list gives us the number of unique items following u
            if ' ' in u:
                lambd *= 0.7 #words with spaces should be taken as less likely
            if w in self.gram_counts[u]:
                return lambd*(self.gram_counts[u][w]/self.total_counts[u]) + (1.0-lambd)*self.smoothing(w, u[1:])
            else:
                return 0.5*(1.0-lambd)*self.smoothing(w, u[1:]) #the other probability is 0 
        else:
            return 0.5*self.smoothing(w, u[1:]) #return the next probability, since lambda will be 0 (using discounting)
            #also penalize partial matches with 0.5

    def prob(self, w):
        """Return the probability of the next character being w given the
        current state."""
        return self.smoothing(w, self.s)
