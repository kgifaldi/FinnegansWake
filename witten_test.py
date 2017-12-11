import wittenmod
import os
#from polyglot.detect import Detector


def search_line(line, e_m, f_m, ofile): #TODO: make sure we can change grams
    """search line for notable things to output"""
    best_p= [] #highest probability moments
    last = 100
    for i, w in enumerate(line.rstrip('\n')):
        prob_j = e_m.prob(w) #probability that joyce was writing English
        prob = f_m.prob(w) #probability of this character in f
        if prob > 0.95 and prob_j < 0.5 and abs(last-i) > f_m.n/2: #want letters to be somewhat far apart
            best_p.append((i, prob))
            last = i
        e_m.read(w)
        f_m.read(w)
    if best_p:
        ofile.write(line)
        for best, max_p in best_p:
            l = best - f_m.n #get index of best match
            if best - f_m.n < 0:
                l = 0  
            if best-l > 2: #don't want short segments at beginning of sentences
                ofile.write(line.rstrip('\n')[l:best + 1] + '\n')
        ofile.write('\n')

def main():

    """Program to train and test the fivegram model"""

    n = 5

    e_m = wittenmod.Wittengram(n)
    print("joyce")
    for tfile in os.listdir("./langs/joyce"):
        e_m.train("./langs/joyce/" + tfile)
        print(tfile + "...")
    e_m.start()

    g_m = wittenmod.Wittengram(n)
    print("German")
    for tfile in os.listdir("./langs/german"):
        g_m.train("./langs/german/" + tfile)
        print(tfile + "...")
    g_m.start()

    i_m = wittenmod.Wittengram(n)
    print("Irish")
    for tfile in os.listdir("./langs/irish"):
        i_m.train("./langs/irish/" + tfile)
        print(tfile + "...")
    i_m.start()

    f_m = wittenmod.Wittengram(n)
    print("French")
    for tfile in os.listdir("./langs/french"):
        print(tfile + "...")
        f_m.train("./langs/french/" + tfile)
    f_m.start()
 
    with open("langs/finnegans.txt") as tfile, open("output/french", "w") as ffile, open("output/german", "w") as gfile, open("output/irish", "w") as ifile:
        for line in tfile:
            search_line(line, e_m, g_m, gfile)
            search_line(line, e_m, f_m, ffile)
            search_line(line, e_m, i_m, ifile)
            #incorporate new data to model (necessary to keep track of grams)


if __name__ == "__main__":
    main()
