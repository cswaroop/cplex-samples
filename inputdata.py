#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: inputdata.py
# Version 12.6
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
# Copyright IBM Corporation 2009, 2013. All Rights Reserved.
# 
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ---------------------------------------------------------------------------
#
# utility for reading data from .dat files in examples/data/.

"""Read data from a .dat file."""


def get_words(line):
    """Return a list of the tokens in line."""
    line = line.replace("\t", " ")
    line = line.replace("\v", " ")
    line = line.replace("\r", " ")
    line = line.replace("\n", " ")
    while line.count("  "):
        line = line.replace("  ", " ")
    line = line.strip()
    return [word + " " for word in line.split(" ")]


def read_dat_file(filename):
    """Return a list containing the data stored in the dat file.

    Single integers or floats are stored as their natural type.

    1-d arrays are stored as lists
    
    2-d arrays are stored as lists of lists.
    
    NOTE: the 2-d arrays are not in the list-of-lists matrix format
    that the python methods take as input for constraints.

    """
    f = open(filename)
    ret = []
    continuation = False
    for line in f:
        for word in get_words(line):
            if continuation:
                entity = "".join([entity, word])
            else:
                entity = word
            try:
                ret.append(eval(entity))
                continuation = False
            except SyntaxError:
                continuation = True
    return ret


