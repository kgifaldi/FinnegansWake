try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
from io import BytesIO
from collections import defaultdict
import pycurl
from fuzzywuzzy import fuzz

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.even_tr = False
        self.in_tr = False
        self.phrase_wordpair = defaultdict(lambda: [])
        self.save_data = False
        self.data_string = ""
        self.langs = ["German", "French", "Irish"]
        self.is_phrase = False
        self.curr_phrase = ""
        self.other_lang = False
        self.tags = []
    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.in_td = True
            self.even_tr = not self.even_tr
            self.handle_data(attrs)
        self.tags.append(tag)
    def handle_endtag(self, tag):
        if tag == "td":
            self.in_td = False
        self.tags.pop()
    def handle_data(self, data):
        #if self.in_td:
        if self.is_phrase:
            self.is_phrase = False
            self.curr_phrase = data.strip()
            if ':' not in data.strip():
                self.data_string += str("\n\n" + data.strip())
            else:
                self.data_string += str("\n" + data.strip())
        elif self.tags and self.tags[-1] == "td":
            self.data_string += str("\n" + data.strip())
            self.phrase_wordpair[self.curr_phrase].append(data.strip())
        if data == [('class', 'grep_fwt')]:
            self.is_phrase = True

def parse(url):
    # first curl the html data from fweet
    curl = pycurl.Curl()
    html_buffer = BytesIO()
    curl.setopt(curl.URL, str(url))
    curl.setopt(curl.WRITEDATA, html_buffer)
    print("URL: ", url)
    curl.perform()
    curl.close()

    html = html_buffer.getvalue()

    # now we need to parse the html for the important stuff
    parser = MyHTMLParser()
    parser.feed(html)
    return parser.phrase_wordpair

def calculate_f1(lang_dict, filename):
    is_phrase = False
    initial = True
    curr_phrase = ""
    curr_translations = []
    tp = 0
    fn = 0
    fp = 0
    phrases = set()
    first_blank = True
    for line in filename:
        if is_phrase or initial:
            initial = False
            is_phrase = False
            curr_phrase = line.rstrip()
            phrases.add(curr_phrase)
            first_blank = True
        else:
            curr_translations.append(line.strip())
        if not line.strip() and first_blank:
            first_blank = False
            # end of line translation evaluate
            if curr_phrase in lang_dict:
                matched = [False]*len(lang_dict[curr_phrase]) #check off true data when matched
                for trans1 in curr_translations:
                    found_match = False
                    for i, trans2 in enumerate(lang_dict[curr_phrase]):
                        rat = fuzz.partial_ratio(trans1, trans2)
                        if rat > 50 and not matched[i]:
                            tp += 1
                            matched[i] = True
                            found_match = True
                            break
                    if not found_match: #no match in annotations
                        fp += 1
                for b in matched:
                    if not b:
                        fn += 1
            else:
                fp += len(curr_translations)

            is_phrase = True
            curr_translations = []

    for line in lang_dict:
        if line not in phrases:
            fn += len(lang_dict[line])
    if (tp+fp) and (tp+fn):
        precision = float(tp / float(tp+fp))
        recall = float(tp/float((tp+fn)))
        f1 = float(2*float(precision*recall)/(precision+recall))
    elif (tp+fp):
        precision = float(tp / float(tp+fp))
        recall = 0
        f1 = 0
    else:
        precision = 0
        recall = float(tp/float((tp+fn)))
        f1 = 0
    print "Precision: ", precision
    print "Recall: ", recall
    print "F1 score: ", f1

if __name__ == "__main__":

    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_G_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    german_dict = parse(url)
    german_file = open("./output/german", "r")
    print "German Simple F1: "
    calculate_f1(german_dict, german_file)
    german_file = open("./output/german_NN", "r")
    print "German Neural Network F1: "
    calculate_f1(german_dict, german_file)
    german_file = open("./output/german_NNT", "r")
    print "German Neural Network Tagged F1: "
    calculate_f1(german_dict, german_file)


    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_F_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    french_dict = parse(url)
    french_file = open("./output/french", "r")
    print "French Simple F1: "
    calculate_f1(french_dict, french_file)
    french_file = open("./output/french_NN", "r")
    print "French Neural Network F1: "
    calculate_f1(french_dict, french_file)
    french_file = open("./output/french_NNT", "r")
    print "French Neural Network Tagged F1: "
    calculate_f1(french_dict, french_file)

    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_I_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    irish_dict = parse(url)
    irish_file = open("./output/irish", "r")
    print "French Simple F1: "
    calculate_f1(irish_dict, irish_file)
    irish_file = open("./output/irish_NN", "r")
    print "French Neural Network F1: "
    calculate_f1(irish_dict, irish_file)
    irish_file = open("./output/irish_NNT", "r")
    print "French Neural Network Tagged F1: "
    calculate_f1(irish_dict, irish_file)

