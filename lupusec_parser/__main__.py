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

import lupusec_parser
import argparse

def get_arguments():
    parser = argparse.ArgumentParser("LupusecParser: Command Line Utility")
    _add_argument(parser, '-u', '--username', 'Username for Lupusec UI')
    _add_argument(parser, '-p', '--password', 'Password for Lupusec UI')
    _add_argument(parser, '-a', '--address', 'Lupus panel http Lupusec adress')

    parser.add_argument(
        '-t', '--time',
        help='time until the recognition stops',
        type=int,
        required=False,
        default=5)
    return parser.parse_args()

def _add_argument(parser, argument, argument_long, help, required=True):
    parser.add_argument(
        argument, argument_long,
        help=help,
        required=required)

def call():
    args = get_arguments()
    lupusec_parser.gatherInformation(args.address, args.username, args.password, args.time)
  

def main():
    call()

if __name__ == '__main__':
    main()