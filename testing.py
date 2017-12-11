try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
from io import BytesIO
from collections import defaultdict
import pycurl

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.even_tr = False # dont matter
        self.in_tr = False # dont matter
        self.phrase_wordpair = defaultdict(lambda: ("","")) # dont matter
        self.save_data = False
        self.data_string = ""
        self.langs = ["German", "French"]
        self.is_phrase = False
    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.in_td = True # dont matter
            self.even_tr = not self.even_tr # dont matter
            print("tag: ", tag) # dont matter
            self.handle_data(attrs)
    def handle_endtag(self, tag):
        if tag == "td": # dont matter
            self.in_td = False # dont matter
    def handle_data(self, data):
        if self.save_data and data not in self.langs:
            if self.is_phrase:
                self.data_string += str("\n" + data.strip())
                print("saving data: ", data.strip())
            else:
                self.data_string += str("\n-" + data.strip())
                print("saving data: -", data.strip())
            self.save_data = False
            self.is_phrase = False
        if isinstance(data, list):
            self.save_data = True
            self.is_phrase = True
        if data in self.langs:
            self.save_data = True
            self.is_phrase = False
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
    return parser.data_string

if __name__ == "__main__":

    #lang_list = ["G", "F"] # ["I", "D", "Jp"]
    #for lang in lang_list:

    save_file = "german_phrases.txt"
    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_G_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    fp = open(save_file, "w").close()
    fp = open(save_file, "w")
    fp.write(parse(url))

    save_file = "french_phrases.txt"
    url = str("http://fweet.org/cgi-bin/fw_grep.cgi?srch=_F_&cake=&icase=1&accent=1&beauty=1&hilight=1&showtxt=1&escope=1&rscope=1&dist=4&ndist=4&fontsz=100&shorth=1")
    fp = open(save_file, "w").close()
    fp = open(save_file, "w")
    fp.write(parse(url))
