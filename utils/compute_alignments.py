import logging
import sys
from collections import deque
import argparse
from functools import partial
from itertools import product

# Source: https://johnlekberg.com/blog/2020-10-25-seq-align.html

prog = 'compute_alignments'
__version__ = "0.0.1"

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
        src_unaligned = 0
        tgt_unaligned = 0
        src_upos = {}  # src unaligned POS counts
        tgt_upos = {}  # tgt unaligned POS counts

        for ref, hyp in zip(ref_file, hyp_file):
            ref_tok = ref.split(" ")
            hyp_tok = hyp.split(" ")

            # align with surface forms
            ref_w = [x.split('_')[0] for x in ref_tok]
            hyp_w = [x.split('_')[0] for x in hyp_tok]

            b = align_fast(ref_w, hyp_w)
            total_aligned += len(b)
            # print(f'Alignments: {list(a)}')
            # print(f'Alignment: {list(b)}')

            for tup in b:
                if tup[0] is None:
                    ut = hyp_tok[tup[1]]
                    utp = ut.split('_')[1]
                    print(f'{ctr} Target unaligned: {tup} :: {hyp_tok[tup[1]]} {utp}')
                    tgt_unaligned += 1

                    # increment tgt pos for this token
                    if utp not in tgt_upos:
                        tgt_upos[utp] = 0
                    tgt_upos[utp] += 1

                if tup[1] is None:
                    ut = ref_tok[tup[0]]
                    utp = ut.split('_')[1]
                    print(f'{ctr} Source unaligned: {tup} :: {ref_tok[tup[0]]}')
                    src_unaligned += 1

                    # increment tgt pos for this token
                    if utp not in src_upos:
                        src_upos[utp] = 0
                    src_upos[utp] += 1

            ctr +=1
            # f
            # ind unaligned...

            # print_alignment(ref_w, hyp_w, b)
        log.debug(f'total alignments:\t{total_aligned}')
        log.debug(f'source unaligned:\t{src_unaligned}')
        log.debug(f'target unaligned:\t{tgt_unaligned}')

        log.debug('Unaligned source word POS:')
        for k, v in [(k, v) for k, v in sorted(src_upos.items(), key=lambda item: item[1], reverse=True)]:
            log.debug(f'{k}\t{v}')

        log.debug('Unaligned target word POS:')
        for k, v in [(k, v) for k, v in sorted(tgt_upos.items(), key=lambda item: item[1], reverse=True)]:
            log.debug(f'{k}\t{v}')