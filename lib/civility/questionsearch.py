#!/usr/bin/env python

import sys
from irclog2html.xchatlogsplit import readxchatlogs
from irclog2html.irclog2html import LogParser


def main(argv=sys.argv):
    filename = argv[1]
    print "### %s" % filename

    """ 
    # get a normalized timestamp for each line
    for date, line in readxchatlogs(file(filename)):
        print date," --- ",line
    """

    #import epdb; epdb.st()
    x = LogParser(filename)
    #import epdb; epdb.st()



if __name__ == "__main__":
    main()
