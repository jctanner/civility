#!/usr/bin/env python

# https://gist.github.com/Tatsh/5793797

import argparse
import datetime
import glob
import json as JSON
import os
import re
import sys
from dateutil import parser as date_parser, tz

# Usage: ./parse-xchat-logs.py -t '-0500' DIRECTORY_TO_LOG_FILES
# X-Chat 2/HexChat log parser
# From Preferences > Logging (without quotes):
#   Log filename: '%n/%Y%m%d-%c.log'
#   Log timestamp foramt: '%b %d %H:%M:%S '

# This also supports the file name format: '%c-%y%m%d.log' (2-digit year suffix (after '20'), example: ##asm-071203.log)

FILENAME_REGEX = r'^(?:20(?P<year1>\d{2})\d{2}[^\-]+\-(?P<channel1>\#[^\.]+))|(?:(?P<channel2>\#[^\-]+)\-(?P<year2>\d{2}))'
USER_MESSAGE_REGEX = r'(?P<date>^[A-Z][a-z]{2}\s+\d+\s+(?:\d{2}\:?){3})\s+<(?P<nick>[^>]+)>\s+(?P<message>.*)'
CHANNEL_MESSAGE_REGEX = r'(?P<date>^[A-Z][a-z]{2}\s+\d+\s+(?:\d{2}\:?){3})\s+\*\t(?P<message>[^\ ]+)\s(.*)'

JSON.encode = JSON.dumps
JSON.decode = JSON.loads


def datetime_to_utc(date):
    """Returns date in UTC without tzinfo"""
    return date.astimezone(tz.gettz('UTC')).replace(tzinfo=None) if date.tzinfo else date

def xchatlog_to_dict(filename):

    return_dict = {}

    network_name = os.path.basename(filename)
    base_filename = os.path.basename(filename)
    collection_name = os.path.basename(os.path.abspath(filename + '/../..'))

    channel = None
    if "#" in base_filename:
        words = base_filename.split("#")
        channel = words[-1]
        channel = channel.replace(".txt", "").replace(".log", "")
        network = words[0]
 


    with open(filename) as f:
        line_no = 1
        log_filename = collection_name + '/' + network_name + '/' + base_filename

        for line in f.readlines():
            line = line.strip()
            message_id = '%d' % (line_no)

            match = re.match(USER_MESSAGE_REGEX, line)

            if match:
                dict = match.groupdict()
                urls_found = []

                for word in dict['message'].split():
                    if 'http://' in word or 'https://' in word:
                        urls_found.append(word)

                data = {
                        'channel': channel,
                        'date_created': None,
                        'is_slash_me': False,
                        'nick': dict['nick'],
                        'message': dict['message'],
                        'line_number': line_no,
                        'network': network,
                        'urls': urls_found,
                        'collection': collection_name,
                        'log_file': log_filename,
                }

                return_dict[message_id] = data

            line_no += 1

    return return_dict


if __name__ == '__main__':

    pass
