#!/bin/bash

# Purpose: Find the average number of words per line in a text

# Assumptions: A word is a string of characters separated by white
# space. Every line should be used in the calculation (i.e. there are
# no empty lines

# Usage: $ awk -f THISFILE input.txt

{
    t += NF
}

END{
    print t/NR
}