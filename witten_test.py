import wittenmod

if __name__ == "__main__":

    """Program to train and test the fivegram model"""

    #e_m = wittengram.Wittengram()
    #e_m.train("langs/english")
    #e_m.start()
    print("1")
    g_m = wittenmod.Wittengram()
    print("2")
    g_m.train("German")
    print("3")
    g_m.start()
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


    count = 0
    for line in open("langs/finnegans.txt"):
        max_p = 0.0
        best = 0
        for i, w in enumerate(line.rstrip('\n')):
            prob = g_m.prob(w) #probability of this character in german
            if prob > max_p:
                max_p = prob
                best = i
            g_m.read(w)
        l = best - 5 #get index of best match
        if best - 5 < 0:
            l = 0
        if max_p > 0.99:
            print('-*-')
            print(line.rstrip('\n'))
            print(line.rstrip('\n')[l:best + 1], max_p)
            print(' ')
            count += 1
            #incorporate new data to model (necessary to keep track of grams)
    print("lines: " + str(count))
