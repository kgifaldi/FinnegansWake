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
            print("tag: ", tag)
            self.handle_data(attrs)
        self.tags.append(tag)
    def handle_endtag(self, tag):
        if tag == "td":
            self.in_td = False
        self.tags.pop()
    def handle_data(self, data):
        #if self.in_td:
        if self.is_phrase:
            print("phrase: ", data)
            self.is_phrase = False
            self.curr_phrase = data.strip()
            if ':' not in data.strip():
                self.data_string += str("\n\n" + data.strip())
            else:
                self.data_string += str("\n" + data.strip())
        elif self.tags and self.tags[-1] == "td":
            print("word: ", data)
            self.data_string += str("\n" + data.strip())
            self.phrase_wordpair.append(data.strip())
        if data == [('class', 'grep_fwt')]:
            self.is_phrase = True

        #if isinstance(data, list):
        #    self.save_data = True
        #    self.is_phrase = True

        '''
        if self.save_data and data not in self.langs:
            if self.is_phrase:
                self.data_string += str("\n\n" + data.strip())
                print("saving data: ", data.strip())
                self.curr_phrase = str(data.strip())
            #elif self.other_lang:
            else:
                print("DATA IN QUESTION: ", data)
                if ':' in data.strip():
                    self.data_string += str("\n" + data.strip().split(':')[0])
                    print("saving data: -", data.strip().split(':')[0])
                    self.phrase_wordpair[self.curr_phrase].append(data.strip().split(':')[0]) # stored like: key: phrase: value list["ran:tran","this:that"]
                    self.other_lang = False
            self.save_data = False
            self.is_phrase = False
        elif data in self.langs:
            print("data list: ", data)
            self.other_lang = True
            self.is_phrase = False
        if isinstance(data, list):
            self.save_data = True
            self.is_phrase = True
        if data in self.langs:
            self.save_data = True
            self.is_phrase = False
        '''
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
    for line in filename:
        if is_phrase or initial:
            initial = False
            is_phrase = False
            curr_phrase = line.rstrip()
            phrases.add(curr_phrase)
        else:
            curr_translations.append(line.strip())
        if not line.strip():
            # end of line translation evaluate
            if curr_phrase in lang_dict:
                matched = [False]*len(lang_dict[curr_phrase]) #check off true data when matched
                for trans1 in curr_translations:
                    for i, trans2 in enumerate(lang_dict[curr_phrase]):
                        rat = fuzz.partial_ration(trans1, trans2)
                        if rat < 60 or matched[i]:
                            fp += 1
                        else:
                            tp += 1
                        matched[i] = True
                for b in matched:
                    if not b:
                        fn += 1
            else:
                fp += len(curr_translations)

            is_phrase = True
            curr_translations = []

    for line in lang_dict:
        if line not in phrases:
            fn += len(lang_dict(line))

    precision = float(tp / float(tp+fp))
    recall = float(tp/(tp+fn))
    f1 = float(2*float(precision*recall)/(precision+recall))
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1 score: ", f1)

if __name__ == "__main__":

    #lang_list = ["G", "F"] # ["I", "D", "Jp"]
    #for lang in lang_list:

    #save_file = "german_phrases.txt"
    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_G_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")

    german_dict = parse(url)

    #fp = open(save_file, "w").close()
    #    fp = open(save_file, "w")
    #fp.write(parse(url))



    #save_file = "french_phrases.txt"
    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_F_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    french_dict = parse(url)
    #fp = open(save_file, "w").close()
    #fp = open(save_file, "w")
    #fp.write(parse(url))


    #save_file = "irish_phrases.txt"
    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_I_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    irish_dict = parse(url)

    #fp = open(save_file, "w").close()
    #    fp = open(save_file, "w")
    #fp.write(parse(url))

    irish_file = open("./output/irish", "r")
    calculate_f1(irish_dict, irish_file)



