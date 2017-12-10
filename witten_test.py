import wittenmod
#from polyglot.detect import Detector

if __name__ == "__main__":

    """Program to train and test the fivegram model"""

    e_m = wittenmod.Wittengram()
    print("1")
    e_m.train("langs/joyce/2814-0.txt")
    print("...")
    e_m.train("langs/joyce/4217-0.txt")
    print("...")
    e_m.train("langs/joyce/4300-0.txt")
    print("...")
    e_m.train("langs/joyce/55945-0.txt")
    print("...")
    e_m.train("langs/joyce/pg2817.txt")
    print("...")
    e_m.start()

    g_m = wittenmod.Wittengram()
    print("2")
    g_m.train("German")
    print("...")
    g_m.train("langs/german/pg6698.txt") 
    print("...")
    g_m.train("langs/german/pg27769.txt")
    g_m.start()
    print("3")
    print("4")

    #i_m = wittengram.Wittengram()
    #i_m.train("langs/irish")
    #i_m.start()

    #f_m = wittengram.Wittengram()
    #f_m.train("langs/french")
    #f_m.start()

    #d_m = wittengram.Wittengram()
    #d_m.train("langs/danish")
    #d_m.start()


    count = 0 #count of lines matching this language
    for line in open("langs/finnegans.txt"):
        #max_p = 0.0 #find moment with highest character prob
        best_p= []
        for i, w in enumerate(line.rstrip('\n')):
            prob_j = e_m.prob(w) #probability that joyce was writing English
            prob = g_m.prob(w) #probability of this character in German
            if prob > 0.90 and prob_j < 0.4:
                best_p.append((i, prob))
            g_m.read(w)
            e_m.read(w)
        if best_p:
            print('-*-')
            print(line.rstrip('\n'))
            count += 1 # count lines
            for best, max_p in best_p:
                l = best - 5 #get index of best match
                if best - 5 < 0:
                    l = 0  
                print(line.rstrip('\n')[l:best + 1], max_p)
            print(' ')
            #incorporate new data to model (necessary to keep track of grams)
    print("lines: " + str(count))
