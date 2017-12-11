import wittenmod
import os
#from polyglot.detect import Detector


def search_line(line, e_m, f_m, ofile):
    """search line for notable things to output"""
    best_p= [] #highest probability moments
    for i, w in enumerate(line.rstrip('\n')):
        prob_j = e_m.prob(w) #probability that joyce was writing English
        prob = f_m.prob(w) #probability of this character in f
        if prob > 0.90 and prob_j < 0.4:
            best_p.append((i, prob))
        e_m.read(w)
        f_m.read(w)
    if best_p:
        ofile.write(line)
        for best, max_p in best_p:
            l = best - 5 #get index of best match
            if best - 5 < 0:
                l = 0  
            ofile.write(line.rstrip('\n')[l:best + 1] + '\n')
        ofile.write('\n')

def main():

    """Program to train and test the fivegram model"""

    e_m = wittenmod.Wittengram()
    print("joyce")
    for tfile in os.listdir("./langs/joyce"):
        e_m.train("./langs/joyce/" + tfile)
        print(tfile + "...")
    e_m.start()

    g_m = wittenmod.Wittengram()
    print("German")
    for tfile in os.listdir("./langs/german"):
        g_m.train("./langs/german/" + tfile)
        print(tfile + "...")
    g_m.start()

    i_m = wittenmod.Wittengram()
    print("Irish")
    for tfile in os.listdir("./langs/irish"):
        i_m.train("./langs/irish/" + tfile)
        print(tfile + "...")
    i_m.start()

    f_m = wittenmod.Wittengram()
    print("French")
    for tfile in os.listdir("./langs/french/"):
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
