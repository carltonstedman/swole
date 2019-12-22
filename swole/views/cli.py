#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool to load program from YAML and print out progression for lifting."""
from __future__ import absolute_import, division, print_function

import argparse

# this package
import swole


# ENTRYPOINT ##########


def main():
    parser = argparse.ArgumentParser(description='Lifting progression tool')
    parser.add_argument('program', type=argparse.FileType('r'))
    parser.add_argument('--round', default=5, help='Round to nearest value', type=float)
    parser.add_argument('--table', action='store_true', help='Print tabular output.')
    parser.add_argument('--tm', default=None, help='Training max')
    args = parser.parse_args()

    program = swole.load_program(args.program)
    if bool(args.table):
        program.present_table(rounding=args.round, tm=args.tm)
    else:
        program.present(rounding=args.round, tm=args.tm)


if __name__ == '__main__':
    main()
