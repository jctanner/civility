#!/usr/bin/env python

import os
import sys
import argparse
import pprint
from log_parser_xchat import xchatlog_to_dict



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to logfile')    
    parser.add_argument('--no-cache', action="store_true", help='do not load data from cache')
    args = parser.parse_args()

    logdata = xchatlog_to_dict(args.path)

    pprint.pprint(logdata)


if __name__ == "__main__":
    main()

