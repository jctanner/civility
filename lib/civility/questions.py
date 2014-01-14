#!/usr/bin/env python

# http://stackoverflow.com/questions/2923420/fuzzy-string-matching-algorithm-in-python
# http://stackoverflow.com/questions/682367/good-python-modules-for-fuzzy-string-comparison

import epdb
import os
import sys
import shlex
import re
import Levenshtein
import cPickle as pickle

blacklist = ['are you',
             'understand the question',
             'are you trying to',
             'version of ansible',
             'ansible version',
             'do you want to do',
             'can you give',
             'how would i do that',
             'what do you mean',
             'do you have',
             'do that',
             'for that',
             'did you',
             'for it',
             'have you',
             'what about',
             'go about that'
             'you provide an example',
             'can i ask',
             'can i see',
             'tell me'
             'what you want to do',
             'what does it do',
             'how to fix this',
             'doing that']


def stripircline(line):
    #Dec 18 16:27:08 <jtanner>  got it?
    #got it?

    line = line.replace('"', '')
    line = line.replace("'", "")

    words = shlex.split(line)
    del words[0:3]

    # <BubbaH57> so I get a False in one spot,
    if words[0].startswith("<") and words[0].endswith(">") :
        del words[0]

    if words[0].endswith(':'):
        del words[0]

    newline = ' '.join(words)
    return newline

def sortquestions(questions):
    key_index = []
    for k in questions.keys():
        if 'alternatives' in questions[k]:
            key_index.append((k, len(questions[k]['alternatives'])))        
        else:
            key_index.append((k, 0))

    #sorted_by_second = sorted(data, key=lambda tup: tup[1]
    print "sorting"
    key_index = sorted(key_index, key=lambda tup: tup[1])
    print "reversing"
    key_index.reverse()

    #epdb.st()
    f = open("/tmp/results.txt", "a")

    for q in key_index:
        thiskey = q[0]
        thiscount = q[1]

        black_listed = False
        for b in blacklist:
            if b in thiskey:
                black_listed = True

        #epdb.st()

        if black_listed:
            continue

        print "# %s" % thiskey
        f.write("# %s\n" % thiskey)
        if 'alternatives' in questions[thiskey]:
            for a in questions[thiskey]['alternatives']:
                print "\t %s" % a
                f.write("\t %s\n" % a)

    f.close()

def loadlog(logfile, use_cache=False):
    cache_file = "/tmp/question.pickle"
    logfile = sys.argv[1]
    if not os.path.isfile(logfile):
        print "invalid filename: %s" % logfile
        sys.exit(1)

    if not use_cache:
        filedata = open(logfile, "r").read()
        lines = filedata.split("\n")

        questions = {}

        for line in lines:
            if line.endswith("?"):

                thisline = stripircline(line).lower().replace('?', '')
                print thisline
                sorted_line = ' '.join(sorted(shlex.split(thisline))).strip().replace('?', '')

                if len(thisline.split()) > 5:
                    #print line
                    if questions == {}:
                        questions[thisline] = {}
                    else:
                        for k in questions.keys():
                            thisratio = Levenshtein.ratio(k, thisline)
                            #thisratio = Levenshtein.ratio(''.join(sorted(k)), sorted_line)
                            if thisratio >= 0.8 and thisratio < 1.0:
                                #print "possible match? %s" % str(thisratio)
                                #print "A: ",k
                                #print "B: ",thisline
                                if 'alternatives' not in questions[k]:
                                    questions[k]['alternatives'] = []
                                questions[k]['alternatives'].append(thisline)
                            else:

                                #sorted_line = ' '.join(sorted(shlex.split(thisline))).strip().replace('?', '')

                                if 'sorted_key' not in questions[k]:
                                    questions[k]['sorted_key'] =  \
                                        ' '.join(sorted(shlex.split(k))).strip().replace('?', '')

                                thisratio = Levenshtein.ratio(questions[k]['sorted_key'], sorted_line)

                                if thisratio >= 0.8:
                                    print thisratio
                                    #epdb.st()
                                    questions[k]['alternatives'].append(thisline)
                                else:
                                    if thisline not in questions: 
                                        questions[thisline] = {}                    
                                    if 'alternatives' not in questions[thisline]:
                                        questions[thisline]['alternatives'] = []
 
        # pickle.dump( favorite_color, open( "save.p", "wb" ) )
        pickle.dump(questions, open(cache_file, "wb"))

    else:
        # favorite_color = pickle.load( open( "save.p", "rb" ) )
        questions = pickle.load(open(cache_file, "rb"))

    print "finished loading questions"
    return questions

#sortquestions(questions)
#epdb.st()                        

if __name__ == "__main__":

    cache_file = "/tmp/question.pickle"
    log_file = sys.argv[1]
    if len(sys.argv) > 2:
        use_cache = sys.argv[2] 
        if str(use_cache) in ['True', 'true', 'yes', '0']:
            use_cache = True
        else:
            use_cache = False
    else:
        use_cache = True
    #epdb.st()
    questions = loadlog(log_file, use_cache=use_cache)
    sortquestions(questions)        
