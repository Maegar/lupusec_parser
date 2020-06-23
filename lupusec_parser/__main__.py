#!/usr/bin/env python3
# Copyright 2020 Paul Proske
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LUPUSEC UI extractor CLI module.

This module is the CLI for the LupusecExtractor 
"""

import lupusec_parser
import argparse

def get_arguments():
    """ Get arguments that we need for CLI """
    parser = argparse.ArgumentParser("LupusecParser: Command Line Utility")
    parser.add_argument('-u', '--username', help='LUsername for Lupusec UI', required=True)
    parser.add_argument('-p', '--password', help='Password for Lupusec UI', required=True)
    parser.add_argument('-a', '--address', help='Lupus panel http Lupusec adress', required=True)
    parser.add_argument('-t', '--time', help='time until the recognition stops', type=int, required=False, default=5)
    return parser.parse_args()

def main():
    """ Main method that will be used if module is started through a command line """
    args = get_arguments()
    extractor = lupusec_parser.LupusecExtractor(args.address, args.username, args.password)
    extractor.gatherInformation(args.time)
    extractor.print_result()

if __name__ == '__main__':
    main()