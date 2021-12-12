__version__ = "0.0.1"

# analyze pos from marked up annotation file
import html
import os
import argparse
from datetime import datetime

import editdistance

from how2diag.posmap import maptagsimple_pt
from how2diag.report import header, footer, posreport, showsent, scoretable

prog = 'analyzepos'


def tupletokenize(sent, maptags=""):

    ret = []
    toks = sent.split()

    # need to apply a map on punc
    # return [tuple(map(str, tok.split('_'))) for tok in toks]

    for tok in toks:
        frag = tok.split('_')
        # tup = (frag[0], maptagsimple_pt(frag[1]))  # mapped

        if maptags == 'pt':
            tup = (frag[0], maptagsimple_pt(frag[1]))  # mapped
        else:
            tup = (frag[0], frag[1])  # not mapped

        if tup[1] == 'UNK':
            print(f'UNK: {tok}')

        ret.append(tup)

    return ret

# return a dict of pos and counts for tokens
def poscount(tups):
    pos = {}
    for tup in tups:
        if tup[1] in pos.keys():
            pos[tup[1]] += 1
        else:
            pos[tup[1]] = 1

    return pos


# Accumulate parts of speech for global recording
# modifies input params
def accumulatepos(total, part):

    # iterate over part keys and add/increment to total
    for k, v in part.items():
        if k in total.keys():
            total[k] += v
        else:
            total[k] = 1


def calceditdist(reftok, t1tok, t2tok):

    # stackoverflow says this will unzip lists of tuples...
    refwords, refpos = zip(*reftok)
    t1words, t1pos = zip(*t1tok)
    t2words, t2pos = zip(*t2tok)

    # lol variable shadowing
    _t1lev = editdistance.eval(refwords, t1words)
    _t1poslev = editdistance.eval(refpos, t1pos)

    _t2lev = editdistance.eval(refwords, t2words)
    _t2poslev = editdistance.eval(refpos, t2pos)

    return _t1lev, _t1poslev, _t2lev, _t2poslev


# Given a list of dicts with POS info, find the superset of the tags

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=prog)

    parser.add_argument("-a", "--annot", help="annotation file")
    # language flag to collapse different POStag sets, default to en
    parser.add_argument("-l", "--lang", help="translation output 1", default="en")
    parser.add_argument("-L", "--limit", help="limit processing to n (dbg)", type=int, default=0)
    parser.add_argument("-r", "--report", help="report output directory", default="analyzereport")
    parser.add_argument("--map-tgt", help="map tgt ref/t1/t2 postags (lang)", default="")

    # buffers for corpus bleu
    args = parser.parse_args()

    # make report dir and sent subdir if not exist
    os.makedirs(f'{args.report}/sents', exist_ok=True)

    with open(f'{args.annot}') as annot, open(f'{args.report}/index.html', "w") as report, open(f'{args.report}/sentlist.html', 'w') as sentlist:
        ctr = 0

        # write report index header
        header(report, f'Analysis for: {args.annot}')

        report.write('<p><a href="index.html">Summary</a> | <a href="sentlist.html"> Sentence List</a></p>\n')

        progstats = {
            prog: __version__,
            'runtime': datetime.now(),
            'annot file': args.annot,
            'tagset lang': args.lang,
            'report dir': args.report
        }
        scoretable(report, progstats)

        # report.write(f'<p>{prog} {__version__}</p>\n')
        # report.write(f'<p>{datetime.now()}</p>\n')
        # report.write(f'<p>annot:  {args.annot}</p>\n')
        # report.write(f'<p>lang:   {args.lang}</p>\n')
        # report.write(f'<p>report: {args.report}</p>\n\n')

        # write sentence list header
        header(sentlist, f'Sentence List for: {args.annot}')
        sentlist.write('<p><a href="index.html">Summary</a> | <a href="sentlist.html"> Sentence List</a></p>\n')
        sentlist.write('<table border="1">')


        # global accumulators
        totalrefpos = {}
        totalt1pos = {}
        totalt2pos = {}

        totalt1lev = 0
        totalt1poslev = 0
        totalt2lev = 0
        totalt2poslev = 0

        for line in annot:
            ctr += 1

            # Now needs
            lineno, cond, t1bleu, t2bleu, ref, t1hyp, t2hyp, src = line.split('\t')

            # get tokenized tuples for word/pos
            reftok = tupletokenize(ref, args.map_tgt)
            t1tok = tupletokenize(t1hyp, args.map_tgt)
            t2tok = tupletokenize(t2hyp, args.map_tgt)

            # leave source tokens alone
            srctok = tupletokenize(src)

            # get parts of speech
            refcnt = poscount(reftok)
            t1cnt = poscount(t1tok)
            t2cnt = poscount(t2tok)

            # increment totals
            accumulatepos(totalrefpos, refcnt)
            accumulatepos(totalt1pos, t1cnt)
            accumulatepos(totalt2pos, t2cnt)

            # calculate lev. distances
            t1lev, t1poslev, t2lev, t2poslev = calceditdist(reftok, t1tok, t2tok)

            # accumulate for averaging
            totalt1lev += t1lev
            totalt1poslev += t1poslev
            totalt2lev += t2lev
            totalt2poslev += t2poslev

            # write to sentencelist
            sentlist.write(f'<tr><td><a href="sents/{ctr}.html">{ctr}</a></td><td>{html.escape(cond)}</td><td><b>t1:</b> {float(t1bleu):.2f}</td><td><b>t2:</b> {float(t2bleu):.2f}</td><td><b>T1 Lev:</b>{t1lev}</td><td><b>T2 Lev:</b>{t2lev}</td><td><b>src:</b> {" ".join([t[0] for t in srctok[:10]])}...</td></tr>\n')

            # create report page for this sentence
            with open(f'{args.report}/sents/{ctr}.html', 'w') as sreport:

                header(sreport, f'Sentence {ctr}')
                sreport.write('<p><a href="../index.html">Summary</a> | <a href="../sentlist.html"> Sentence List</a></p>\n')
                # t1lev = editdistance.eval(reftok, t1tok)
                # t2lev = editdistance.eval(reftok, t2tok)

                # sentstats table
                sentstats = {
                    'Condition': cond,
                    'T1 Sent Bleu': t1bleu,
                    'T2 Sent Bleu': t2bleu,
                    'Ref vs T1 Lev. Dist:': t1lev,
                    'Ref vs T1 POS Lev Dist:': t1poslev,
                    'Ref vs T2 Lev. Dist:': t2lev,
                    'Ref vs T2 POS Lev Dist:': t2poslev,
                }

                # old way
                # scoretable(sreport, cond, t1bleu, t2bleu, t1lev, t2lev)

                sreport.write('<table><tr><td>\n')
                scoretable(sreport, sentstats)
                # hack for yolo
                sreport.write(f'</td><td><video controls width="320" height="240" preload="metadata"><source src="../../clips/dev5/{ctr}.mp4">foo</video>\n')
                sreport.write(f'</td><td><video controls width="320" height="240" preload="metadata"><source src="../../clips/dev5-yolo/{ctr}.mp4">foo</video></td></tr></table>\n')

                showsent(sreport, srctok, 'Source')
                showsent(sreport, reftok, 'Reference')
                showsent(sreport, t1tok, 'T1 Hyp')
                showsent(sreport, t2tok, 'T2 Hyp')

                sreport.write('<h2>POS Count</h2>\n')
                posreport(sreport, refcnt, t1cnt, t2cnt)

                footer(sreport)

            # stub...
            # analyzecounts(refcnt, t1cnt)

            # print(f'{lineno} {cond} ref: {refcnt} t1: {t1cnt} t2: {t2cnt}')



            if int(args.limit > 0) and (ctr > args.limit):
                break

        # write averaged distance metrics
        report.write('<h2>Average Levenshtein Distances</h2>')
        diststats = {
            'Avg. Ref vs T1 Lev. Dist': float(totalt1lev) / float(ctr),
            'Avg. Ref vs T1 POS Lev. Dist': float(totalt1poslev) / float(ctr),
            'Avg. Ref vs T2 Lev. Dist': float(totalt2lev) / float(ctr),
            'Avg. Ref vs T2 POS Lev. Dist': float(totalt2poslev) / float(ctr),
        }
        scoretable(report, diststats)

        # generate count report for each present pos tag
        report.write('<h2>Total POS counts</h2>')
        posreport(report, totalrefpos, totalt1pos, totalt2pos)

        footer(report)
