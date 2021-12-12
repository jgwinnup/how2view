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

    x = ['A', 'B', 'C', 'D', 'E']
    y = ['A', 'B', 'D', 'C', 'E']

    ref = "O_DA0 aileron_NCMS é_VMI a_DA0 superfície_NCFS de_SPS controle_NCMS na_SP+DA asa_NCFS que_PR0 é_VMI controlada_VMP pelo_SP+DA movimento_NCMS lateral_AQ0 direito_AQ0 e_CC esquerdo_AQ0 do_SPS bastão_NCMS ._Fp"
    hyp = "O_DA0 acompanhante_NCCS é_VMI a_DA0 superfície_NCFS de_SPS controle_NCMS na_SP+DA asa_NCFS que_PR0 é_VMI controlada_VMP pelo_SP+DA movimento_NCMS lateral_AQ0 e_CC a_DA0 esquerda_NCFS do_SPS bastão_NCMS ._Fp "

    with open(args.ref, 'r') as ref_file, open(args.hyp, 'r') as hyp_file, open(args.out, 'w') as outfile:

        for ref, hyp in zip(ref_file, hyp_file):
            ref_tok = ref.split(" ")
            hyp_tok = hyp.split(" ")

            # align with surface forms
            ref_w = [x.split('_')[0] for x in ref_tok]
            hyp_w = [x.split('_')[0] for x in hyp_tok]

            b = align_fast(ref_w, hyp_w)

            # print(f'Alignments: {list(a)}')
            print(f'Alignment: {list(b)}')

            # find unaligned...

            # print_alignment(ref_w, hyp_w, b)
