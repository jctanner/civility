#!/usr/bin/env python

import epdb
import os
import sys
import argparse
import pprint
import cPickle as pickle
from log_parser_xchat import xchatlog_to_dict
from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier



class xchatLog(object):

    def __init__(self, filename, cache=True):
        self.filename = filename
        self.logdata = None
        self.cache = cache
        self.cache_file = None
        self.cache_name_generate()
        self.load_file()


    def load_file(self):

        """ parse file or load from pickle """

        if os.path.isfile(self.cache_file) and self.cache:
            print "loading cached data from: %s" % self.cache_file
            self.logdata = pickle.load(open(self.cache_file, "rb"))        
        else:
            print "reading logfile (%s missing)" % self.cache_file
            self.logdata = xchatlog_to_dict(self.filename)
            self.save_pickle()

    def save_pickle(self):
    
        """ write out pickle data """

        pickle.dump(self.logdata, open(self.cache_file, "wb"))        


    def cache_name_generate(self):

        """ strip the filepath to make a cache filename """

        cache_name = os.path.basename(self.filename)
        cache_name = cache_name.replace("#", "_")
        cache_name = cache_name.replace("-", "")
        cache_name = cache_name.replace(".log", "")
        cache_file = os.path.join("/tmp", cache_name)
        self.cache_file = cache_file
       

    def process_sentiment(self):
        ks = [ int(x) for x in self.logdata.keys() ]
        for k in sorted(ks):
            k_str = str(k)
            #print k, self.logdata[k_str]
            this_msg = self.logdata[k_str]['message']
            text_obj = TextBlob(this_msg)
            #epdb.st()
            try:
                this_polarity, this_subjectivity = \
                    text_obj.sentiment
            except UnicodeDecodeError:
                this_polarity = None
                this_subjectivity = None
        
            #epdb.st()
            if this_polarity is not None and this_subjectivity is not None:
                #if this_polarity > .9 or this_subjectivity < .1:
                if this_polarity < -.7:
                    print k, self.logdata[k_str]
                    print this_polarity,";",this_subjectivity,";",this_msg


    def process_questions(self):
        ks = [ int(x) for x in self.logdata.keys() ]
        for k in sorted(ks):
            k_str = str(k)
            #print k, self.logdata[k_str]
            this_msg = self.logdata[k_str]['message']
            text_obj = TextBlob(this_msg)
            #import epdb; epdb.st() 

            if hasattr(text_obj, "raw_sentences"):
                for sent in text_obj.sentences:
                    if sent.endswith("?"):
                        try:
                            print sent
                        except UnicodeDecodeError:
                            pass

    def show(self):
    
        """ raw print all data """

        pprint.pprint(self.logdata)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to logfile')    
    parser.add_argument('--cache', action="store_true", help='load data from cache')
    args = parser.parse_args()
    
    x = xchatLog(args.path, cache=args.cache)
    #x.show()
    #x.process_sentiment()
    x.process_questions()
    #x.classify()


if __name__ == "__main__":
    main()

