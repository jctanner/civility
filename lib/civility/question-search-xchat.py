#!/usr/bin/env python

import os
import sys
import argparse
import pprint
import cPickle as pickle
from log_parser_xchat import xchatlog_to_dict



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
            print "loading logfile from: %s" % cache_file
            self.logdata = pickle.load(open(cache_file, "rb"))        
        else:
            print "reading logfile"
            self.logdata = xchatlog_to_dict(self.filename)

    def save_pickle(self):
    
        """ write out pickle data """

        pickle.dump(logdata, open(cache_file, "wb"))        


    def cache_name_generate(self):

        """ strip the filepath to make a cache filename """

        cache_name = os.path.basename(self.filename)
        cache_name = cache_name.replace("#", "-")
        cache_name = cache_name.replace(".log", "")
        cache_file = os.path.join("/tmp", cache_name)
        self.cache_file = cache_file
       

    def show(self):
    
        """ raw print all data """

        pprint.pprint(self.logdata)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to logfile')    
    parser.add_argument('--cache', action="store_true", help='load data from cache')
    args = parser.parse_args()
    
    x = xchatLog(args.path, cache=args.cache)
    x.show()


if __name__ == "__main__":
    main()

