import logging
import sys
from collections import deque
import argparse
from functools import partial
from itertools import product

# Alignment Algorithm Source:
# https://johnlekberg.com/blog/2020-10-25-seq-align.html

prog = 'compute_alignments'
__version__ = "0.0.2"

# Common Universal Dependencies POS Tagset
ud_pos_tags = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN',
               'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X']

# compute forced alignments so we can ID danglers
def all_alignments(x, y):
    """Return an iterable of all alignments of two
    sequences.

    x, y -- Sequences.
    """

    def F(x, y):
        """A helper function that recursively builds the
        alignments.

        x, y -- Sequence indices for the original x and y.
        """
        if len(x) == 0 and len(y) == 0:
            yield deque()

        scenarios = []
        if len(x) > 0 and len(y) > 0:
            scenarios.append((x[0], x[1:], y[0], y[1:]))
        if len(x) > 0:
            scenarios.append((x[0], x[1:], None, y))
        if len(y) > 0:
            scenarios.append((None, x, y[0], y[1:]))

        # NOTE: "xh" and "xt" stand for "x-head" and "x-tail",
        # with "head" being the front of the sequence, and
        # "tail" being the rest of the sequence. Similarly for
        # "yh" and "yt".
        for xh, xt, yh, yt in scenarios:
            for alignment in F(xt, yt):
                alignment.appendleft((xh, yh))
                yield alignment

    alignments = F(range(len(x)), range(len(y)))
    return map(list, alignments)


def print_alignment(x, y, alignment):
    print(" ".join(
        "-" if i is None else x[i] for i, _ in alignment
    ))
    print(" ".join(
        "-" if j is None else y[j] for _, j in alignment
    ))


def alignment_score(x, y, alignment):
    """Score an alignment.

    x, y -- sequences.
    alignment -- an alignment of x and y.
    """
    score_gap = -1
    score_same = +1
    score_different = -1

    score = 0
    for i, j in alignment:
        if (i is None) or (j is None):
            score += score_gap
        elif x[i] == y[j]:
            score += score_same
        elif x[i] != y[j]:
            score += score_different

    return score


def align_bf(x, y):
    """Align two sequences, maximizing the
    alignment score, using brute force.

    x, y -- sequences.
    """
    return max(
        all_alignments(x, y),
        key=partial(alignment_score, x, y),
    )


def needleman_wunsch(x, y):
    """Run the Needleman-Wunsch algorithm on two sequences.

    x, y -- sequences.

    Code based on pseudocode in Section 3 of:

    Naveed, Tahir; Siddiqui, Imitaz Saeed; Ahmed, Shaftab.
    "Parallel Needleman-Wunsch Algorithm for Grid." n.d.
    https://upload.wikimedia.org/wikipedia/en/c/c4/ParallelNeedlemanAlgorithm.pdf
    """
    N, M = len(x), len(y)
    s = lambda a, b: int(a == b)

    DIAG = -1, -1
    LEFT = -1, 0
    UP = 0, -1

    # Create tables F and Ptr
    F = {}
    Ptr = {}

    F[-1, -1] = 0
    for i in range(N):
        F[i, -1] = -i
    for j in range(M):
        F[-1, j] = -j

    option_Ptr = DIAG, LEFT, UP
    for i, j in product(range(N), range(M)):
        option_F = (
            F[i - 1, j - 1] + s(x[i], y[j]),
            F[i - 1, j] - 1,
            F[i, j - 1] - 1,
        )
        F[i, j], Ptr[i, j] = max(zip(option_F, option_Ptr))

    # Work backwards from (N - 1, M - 1) to (0, 0)
    # to find the best alignment.
    alignment = deque()
    i, j = N - 1, M - 1
    while i >= 0 and j >= 0:
        direction = Ptr[i, j]
        if direction == DIAG:
            element = i, j
        elif direction == LEFT:
            element = i, None
        elif direction == UP:
            element = None, j
        alignment.appendleft(element)
        di, dj = direction
        i, j = i + di, j + dj
    while i >= 0:
        alignment.appendleft((i, None))
        i -= 1
    while j >= 0:
        alignment.appendleft((None, j))
        j -= 1

    return list(alignment)


def align_fast(x, y):
    """Align two sequences, maximizing the
    alignment score, using the Needleman-Wunsch
    algorithm.

    x, y -- sequences.
    """
    return needleman_wunsch(x, y)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--ref", help="reference file")
    parser.add_argument("--hyp", help="hypothesis file")
    parser.add_argument("--out", help="output file")
    parser.add_argument("--flat", help="Flat format report", default=False, action="store_true")

    args = parser.parse_args()

    # overly fancy logging example
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    output_file_handler = logging.FileHandler(args.out, mode='w')  # overwrite each run
    stdout_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(output_file_handler)
    log.addHandler(stdout_handler)

    with open(args.ref, 'r') as ref_file, open(args.hyp, 'r') as hyp_file:  #, open(args.out, 'w') as outfile:
        ctr = 1
        total_aligned = 0
        ref_unaligned = 0
        hyp_unaligned = 0
        ref_upos = {}  # src unaligned POS counts
        hyp_upos = {}  # tgt unaligned POS counts

        ref_pos = {}  # src total POS counts
        hyp_pos = {}  # tgt total POS counts

        for ref, hyp in zip(ref_file, hyp_file):

            # print(f'ref: {ref}')
            # print(f'hyp: {hyp}')

            # split with no args splits on multiple whitespace
            ref_tok = ref.strip().split() #" ")
            hyp_tok = hyp.strip().split() #" ")

            # align with surface forms
            ref_w = [x.split('_')[0] for x in ref_tok]
            hyp_w = [x.split('_')[0] for x in hyp_tok]

            # global POS count for ratios
            # print(f'{ctr} ref tok: {ref_tok}')
            ref_p = [x.split('_')[1] for x in ref_tok]
            hyp_p = [x.split('_')[1] for x in hyp_tok]

            for p in ref_p:
                if p in ref_pos:
                    ref_pos[p] += 1
                else:
                    ref_pos[p] = 1

            for p in hyp_p:
                if p in hyp_pos:
                    hyp_pos[p] += 1
                else:
                    hyp_pos[p] = 1

            # get alignments for current segment
            b = align_fast(ref_w, hyp_w)
            total_aligned += len(b)
            # print(f'Alignments: {list(a)}')
            # print(f'Alignment: {list(b)}')

            for tup in b:

                if tup[0] is None:
                    ut = hyp_tok[tup[1]]
                    utp = ut.split('_')[1]
                    print(f'{ctr} Target unaligned: {tup} :: {hyp_tok[tup[1]]} {utp}')
                    hyp_unaligned += 1

                    # increment tgt pos for this token
                    if utp not in hyp_upos:
                        hyp_upos[utp] = 0
                    hyp_upos[utp] += 1

                if tup[1] is None:
                    ut = ref_tok[tup[0]]
                    utp = ut.split('_')[1]
                    print(f'{ctr} Source unaligned: {tup} :: {ref_tok[tup[0]]}')
                    ref_unaligned += 1

                    # increment tgt pos for this token
                    if utp not in ref_upos:
                        ref_upos[utp] = 0
                    ref_upos[utp] += 1

            ctr +=1
            # f
            # ind unaligned...

            # print_alignment(ref_w, hyp_w, b)

        # standard verbose report
        if not args.flat:
            log.debug(f'Hypothesis:\t{args.hyp}')
            log.debug(f'Reference:\t{args.ref}')
            log.debug(f'total alignments:\t{total_aligned}')
            log.debug(f'reference unaligned:\t{ref_unaligned}')
            log.debug(f'hypothesis unaligned:\t{hyp_unaligned}')

            log.debug('Reference POS counts:')
            for k, v in [(k, v) for k, v in sorted(ref_pos.items(), key=lambda item: item[1], reverse=True)]:
                log.debug(f'{k}\t{v}')

            log.debug('Hypothesis POS counts:')
            for k, v in [(k, v) for k, v in sorted(hyp_pos.items(), key=lambda item: item[1], reverse=True)]:
                log.debug(f'{k}\t{v}')

            log.debug('Unaligned ref word POS:')
            for k, v in [(k, v) for k, v in sorted(ref_upos.items(), key=lambda item: item[1], reverse=True)]:
                pct = float(v) / float(ref_pos[k])
                log.debug(f'{k}\t{v}\t{pct:.4f}')

            log.debug('Unaligned hyp word POS:')
            for k, v in [(k, v) for k, v in sorted(hyp_upos.items(), key=lambda item: item[1], reverse=True)]:
                pct = float(v) / float(hyp_pos[k])
                log.debug(f'{k}\t{v}\t{pct:.4f}')

        else:
            # ensure they're in the same order
            log.debug('Desc,' + ",".join(ud_pos_tags))

            tc = []
            for tag in ud_pos_tags:
                tc.append(str(ref_pos.get(tag, 0)))
            log.debug('Total Ref Pos,' + ",".join(tc))
            uc = []
            for tag in ud_pos_tags:
                uc.append(str(ref_upos.get(tag, 0)))
            log.debug('Total Ref Unaligned,' + ",".join(uc))
            tc = []
            for tag in ud_pos_tags:
                tc.append(str(hyp_pos.get(tag, 0)))
            log.debug('Total Hyp Pos,' + ",".join(tc))
            uc = []
            for tag in ud_pos_tags:
                uc.append(str(hyp_upos.get(tag, 0)))
            log.debug('Total Hyp Unaligned,' + ",".join(uc))
