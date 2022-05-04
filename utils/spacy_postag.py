#!/usr/bin/env python

import argparse
import spacy
from spacy import displacy
from collections import Counter
import pandas as pd


# Part of speech tag

prog = 'spacy_postag'
version='0.0.1'

# Pandas stuff
# pd.set_option("max_rows", 400)
# pd.set_option("max_colwidth", 400)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="file to annotate")
    parser.add_argument("--outfile", help="file to annotate")
    parser.add_argument("--verbose", help="verbose output", type=bool)

    args = parser.parse_args()

    nlp = spacy.load('pt_core_news_md')

    # load document to annotate
    with open(args.infile, 'r') as infile, open(args.outfile, 'w') as outfile:

        for line in infile:
            doc = nlp(line.strip())

            outlist = [f'{token.text}_{token.pos_}' for token in doc]

            if(args.verbose):
                print(" ".join(outlist))

            outfile.write(" ".join(outlist) + '\n')

                # print(f'{token.text}_{token.pos_} ')

