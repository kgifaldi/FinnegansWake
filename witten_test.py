import wittengram

if __name__ == "__main__":

    """Program to train and test the fivegram model"""

    #e_m = wittengram.Wittengram()
    #e_m.train("langs/english")
    #e_m.start()
    print "1"
    g_m = wittengram.Wittengram()
    print "2"
    g_m.train("langs/german")
    print "3"
    g_m.start()
    print "4"

    #i_m = wittengram.Wittengram()
    #i_m.train("langs/irish")
    #i_m.start()

    #f_m = wittengram.Wittengram()
    #f_m.train("langs/french")
    #f_m.start()

    #d_m = wittengram.Wittengram()
    #d_m.train("langs/danish")
    #d_m.start()


    for line in open("langs/finnegans.txt"):
        for w in line.rstrip('\n'):
            print g_m.prob(w) #gets the likelihood of following current set of characters
            g_m.read(w)
            #incorporate new data to model (necessary to keep track of grams)
