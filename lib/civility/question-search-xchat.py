#!/usr/bin/env python

import epdb
import os
import sys
import argparse
import csv
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
                """
                if this_polarity < -.7:
                    #print k, self.logdata[k_str]
                    print this_polarity,";",this_subjectivity,";",this_msg
                """
                print this_polarity,";",this_subjectivity,";",this_msg


    def _load_training_data(self):
        self.train_file = "/tmp/question_training"
        self.train = []
        self.known_sentences = []
        with open(self.train_file, 'rb') as csvfile:
            rows = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in rows:
                #print row
                sentence = row[0]
                sentence = sentence[1:-1] #strip outside quotes
                category = row[1]
                self.train.append((sentence, category))
                self.known_sentences.append(sentence)
        #sys.exit()                
        if len(self.train) == 0:
            self.train = [
                ("What is a handler?", "g"),
                ("I like to party", "b")
            ]
                                


    def process_questions(self):

        self._load_training_data()

        five_ws = [ "who", "what", "where", "when", "why" ]

        trigger_phrases = [
            "best practice",
            "simplest way"
            "preferred nomenclature",
            "documentation",
            " doc for ",
            "playbook",
            "role",
            "task",
            "play",
            "variable",
            "var",
            "handler",
            "connection",
            "{{",
            "}}",
            "lookup",
            "hang",
            "plugin"
        ]

        train_file = "/tmp/question_training"
        #good_questions = []
        #bad_questsion = []

        cl = NaiveBayesClassifier(self.train)
    
        ks = [ int(x) for x in self.logdata.keys() ]
        for k in sorted(ks):
            k_str = str(k)

            this_msg = self.logdata[k_str]['message']
            text_obj = TextBlob(this_msg)
            #import epdb; epdb.st()

            if hasattr(text_obj, "raw_sentences"):
                for sent in text_obj.sentences:
                    try:
                        str(sent)
                    except UnicodeDecodeError:
                        #import epdb; epdb.st()
                        continue
                    if str(sent) in self.known_sentences:
                        continue
                    if sent.endswith("?") and [ x for x in sent.words if x.lower() in five_ws ]:
                        #import epdb; epdb.st()
                        print "##############################\n"
                        try:
                            print sent
                        except UnicodeDecodeError:
                            print "unicode error"

                        curr_rating = cl.classify(sent)

                        #import epdb; epdb.st()
                        triggered = False
                        for ph in trigger_phrases:
                            if ph in str(sent):
                                triggered = True                            

                        if curr_rating == "b" and triggered:
                            #continue
                            q_string = "\n$ g(ood) question or b(ad) question? (default: %s): " % curr_rating
                            x = raw_input(q_string)                            
                        else:
                            x == curr_rating

                        if x == "":
                            this_tup = [ (str(sent), curr_rating) ]
                            cl.update(this_tup)
                            self.known_sentences.append(sent)
                            open(self.train_file, "a").write("'%s';%s\n" % (sent, curr_rating))
                        elif x == "b" or x =="g":
                            this_tup = [ (str(sent), x) ]
                            cl.update(this_tup)
                            self.known_sentences.append(sent)
                            open(self.train_file, "a").write("'%s';%s\n" % (sent, x))
                        elif x == "break":
                            import epdb; epdb.st()
                        

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

