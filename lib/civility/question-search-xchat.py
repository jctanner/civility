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

import random


class xchatLog(object):

    def __init__(self, filename, cache=True):
        self.filename = filename
        self.train_file = "~/question_training"
        self.train_file = os.path.expanduser(self.train_file)
        self.train = []
        #self.known_sentence_file = os.path.expanduser("~/known_questions")
        #self.known_sentences = []
        self.processed_tuples = {}
        self.processed_tuples_file = os.path.expanduser("processed_tuples")
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
        if os.path.isfile(self.train_file):
            with open(self.train_file, 'rb') as csvfile:
                rows = csv.reader(csvfile, delimiter=';', quotechar='"')
                for row in rows:
                    #print row
                    sentence = row[0]
                    sentence = sentence[1:-1] #strip outside quotes
                    category = row[1]
                    self.train.append((sentence, category))
                    #self.known_sentences.append(sentence)
        else:
            open(self.train_file, "a").close()
        #sys.exit()                
        if len(self.train) == 0:
            self.train = [
                ("What is a handler?", "g"),
                ("I like to party", "b")
            ]

    def _pdump_processed_tuples(self):

        pickle.dump(self.processed_tuples, open(self.processed_tuples_file, "wb"))        

    def _pload_processed_tuples(self):
        if os.path.isfile(self.processed_tuples_file):
            self.processed_tuples = pickle.load(open(self.processed_tuples_file, "rb"))
            return True
        else:
            return False


    def process_questions(self):

        self._load_training_data()
        self._pload_processed_tuples()

        five_ws = [ "who", "what", "where", "when", "why" ]

        trigger_phrases = [
            "best practice",
            "best way",
            "simplest way",
            "preferred nomenclature",
            "preferred location",
            " have any recommendation",
            "exact command",
            "documentation",
            " doc for ",
            " doc about ",
            "tutorial",
            "release",
            "external inventory", "inventory file",
            "playbook", "play", "role", "task", "handler",
            "variable", "var",
            "connection", "async", "accelerate",
            "{{", "}}",
            "lookup", "plugin", "callback",
            "hang",
            "conditional", "when:"
            "group",
            "ec2 module", "route53",
            "fault tolerance",
            "public key"
        ]

        cl = NaiveBayesClassifier(self.train)
    
        ks = [ int(x) for x in self.logdata.keys() ]
        sorted_ks = sorted(ks)
        total_ks = sorted_ks[-1]
        for k in sorted_ks:
            k_str = str(k)
            print total_ks,"-",k_str

            this_msg = self.logdata[k_str]['message']
            text_obj = TextBlob(this_msg)

            if hasattr(text_obj, "raw_sentences"):
                for sent in text_obj.sentences:
                    try:
                        str(sent)
                    except UnicodeDecodeError:
                        #self.known_sentences.append(sent)
                        continue

                    if str(sent) in self.processed_tuples:
                        continue

                    if sent.endswith("?") and [ x for x in sent.words if x.lower() in five_ws ]:

                        curr_rating = cl.classify(sent)

                        triggered = False
                        for ph in trigger_phrases:
                            if ph in str(sent):
                                triggered = True                            

                        this_tuple = (k, sent, curr_rating, triggered)
                        self.processed_tuples[str(sent)] = this_tuple
                        #self.known_sentences.append(str(sent))

        # save what we have
        self._pdump_processed_tuples()

        for pt in self.processed_tuples.keys():        
            print "##############################\n"

            #import epdb; epdb.st()
            k = self.processed_tuples[pt][0]
            sent = self.processed_tuples[pt][1]
            curr_rating = self.processed_tuples[pt][2]
            triggered = self.processed_tuples[pt][3]

            print sent
            print "\n"
            print "rating: %s" % curr_rating
            print "triggered: %s" % triggered

            if ( curr_rating == "b" and triggered ) or ( curr_rating == "g" and not triggered ):
                #continue
                q_string = "\n$ g(ood) question or b(ad) question? (default: %s): " % curr_rating
                x = raw_input(q_string)                            
            else:
                x = str(curr_rating)

            print "\n"

            if x == "":
                this_tup = [ (str(sent), curr_rating) ]
                cl.update(this_tup)
                #self.known_sentences.append(str(sent))
                open(self.train_file, "a").write("'%s';%s\n" % (sent, curr_rating))
            elif x == "b" or x == "g":
                this_tup = [ (str(sent), x) ]
                cl.update(this_tup)
                #self.known_sentences.append(str(sent))
                open(self.train_file, "a").write("'%s';%s\n" % (sent, x))
            elif x == "break":
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

