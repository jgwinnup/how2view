#!/usr/bin/env python3

# Analysis on part of speech outputs from pynmt baselines

import argparse
import sacrebleu as sb

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-r', '--reference', required=True)
parser.add_argument('-s', '--source', required=True)

args = parser.parse_args()

print(f'output: {args.output}')
print(f'ref:    {args.reference}')
print(f'source: {args.source}')

# Table for understanding Portuguese POS tags
# Collapse to simple subset? N, V, P, Det etc

def tupletokenize(sent):
    toks = sent.split()
    return [tuple(map(str, tok.split('_'))) for tok in toks]


# return a dict of pos and counts for tokens
def poscount(tups):
    pos = {}
    for tup in tups:
        if tup[1] in pos.keys():
            pos[tup[1]] += 1
        else:
            pos[tup[1]] = 1

    return pos #.items()

ctr = 1
with open(args.output, 'r') as outfile, open(args.reference, 'r') as reffile, open(args.source, 'r') as sourcefile:
    for outline, refline, srcline in zip(outfile, reffile, sourcefile):

        # strip whitespace
        outline = outline.strip()
        refline = refline.strip()
        srcline = srcline.strip()

        outtoks = tupletokenize(outline)
        reftoks = tupletokenize(refline)
        srctoks = tupletokenize(srcline)

        # calculate sentencebleu
        out_sbleu = sb.sentence_bleu(outline, [refline]).score

        print(f'{ctr} out: {outtoks}')
        print(f'{ctr} ref: {reftoks}')
        print(f'{ctr} src: {srctoks}')

        outposcount = poscount(outtoks)
        refposcount = poscount(reftoks)

        # compute set differences
        outposset = set(outposcount.items())
        refposset = set(refposcount.items())
        diffset = dict(outposset ^ refposset)

        print(f'sbleu:  {out_sbleu:.2f}')
        print(f'refpos: {refposcount}')
        print(f'outpos: {outposcount}')
        print(f'diffset: {diffset}')

        ctr += 1



        # tokenize to




        # debug
        if ctr == 5:
            break