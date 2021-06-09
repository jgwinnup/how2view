import argparse
import sacrebleu as sb
from datetime import datetime

__version__ = "0.0.1"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='oracleceiling')
    parser.add_argument("--ref", help="reference file")
    parser.add_argument("--t1", help="translation output 1")
    parser.add_argument("--t2", help="translation output 2")
    parser.add_argument("--report", help="report output", default="report.txt")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)
    parser.add_argument("-v", "--verbose")

    # optionally output oracle file

    # buffers for corpus bleu
    args = parser.parse_args()oracleceiling 0.0.1
2021-06-08 16:20:45.009942
ref: ../data/dev5/text.pt
t1:  outputs/nmt-en-pt.out.beam6
t2:  outputs/nmt-visual-en-pt.out.beam6

2305 lines
   t1 > t2: 620 (26.8980%)
   t1 < t2: 597 (25.9002%)
 identical: 967 (41.9523%)
same score: 121 (5.2495%)

    t1 sacrebleu: BLEU = 56.24 79.3/62.0/50.0/40.7 (BP = 1.000 ratio = 1.010 hyp_len = 44503 ref_len = 44075)
    t2 sacrebleu: BLEU = 56.18 79.1/61.9/50.1/40.6 (BP = 1.000 ratio = 1.011 hyp_len = 44573 ref_len = 44075)
oracle sacrebleu: BLEU = 58.91 80.7/64.4/53.0/43.8 (BP = 1.000 ratio = 1.010 hyp_len = 44508 ref_len = 44075)
    ref_lines = []
    oracle = []
    t1_lines = []
    t2_lines = []

    # counters
    count = 0
    t1_better = 0
    t2_better = 0
    identical = 0
    equiv_score = 0

    # process file line by line
    with open(args.ref) as ref:
        with open(args.t1) as t1:
            with open(args.t2) as t2:
                with open(args.report, "w") as report:

                    # write header
                    report.write(f'oracleceiling {__version__}\n')
                    report.write(f'{datetime.now()}\n')
                    report.write(f'ref: {args.ref}\n')
                    report.write(f't1:  {args.t1}\n')
                    report.write(f't2:  {args.t2}\n\n')

                    for line in ref:
                        r_line = line.rstrip()
                        t1_line = t1.readline().rstrip()
                        t2_line = t2.readline().rstrip()

                        t1_bleu = sb.sentence_bleu(t1_line, [r_line]).score
                        t2_bleu = sb.sentence_bleu(t2_line, [r_line]).score

                        ref_lines.append(r_line)
                        t1_lines.append(t1_line)
                        t2_lines.append(t2_line)
                        count += 1

                        if t1_bleu > t2_bleu:
                            oracle.append(t1_line)
                            t1_better += 1
                        elif t2_bleu > t1_bleu:
                            oracle.append(t2_line)
                            t2_better += 1
                        else:  # equal
                            # equivalent translation
                            if t1_line == t2_line:
                                oracle.append(t1_line)
                                identical += 1
                            # translations have equal score
                            # maybe be smart about what line?
                            else:
                                oracle.append(t1_line)
                                equiv_score += 1

                        if args.verbose:
                            print(f'{count} ref: {r_line}')
                            print(f'{count} t1:  {t1_bleu} {t1_line}')
                            print(f'{count} t2:  {t2_bleu} {t2_line}')

                    report.write(f'{count} lines\n')
                    report.write(f'   t1 > t2: {t1_better} ({float(t1_better)/float(count)*100.0:0.4f}%)\n')
                    report.write(f'   t1 < t2: {t2_better} ({float(t2_better)/float(count)*100.0:0.4f}%)\n')
                    report.write(f' identical: {identical} ({float(identical) / float(count)*100.0:0.4f}%)\n')
                    report.write(f'same score: {equiv_score} ({float(equiv_score) / float(count)*100.0:0.4f}%)\n\n')
                    print(f'ref: {len(ref_lines)} t1: {len(t1_lines)} t2: {len(t2_lines)}')
                    report.write(f'    t1 sacrebleu: {sb.corpus_bleu(t1_lines, [ref_lines])}\n')
                    report.write(f'    t2 sacrebleu: {sb.corpus_bleu(t2_lines, [ref_lines])}\n')
                    report.write(f'oracle sacrebleu: {sb.corpus_bleu(oracle, [ref_lines])}\n')
