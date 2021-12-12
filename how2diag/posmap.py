#
# Part of speech mapping
#


# Treetagger Portuguese Tags -> Simple POS
# PT Tags: https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/Portuguese-Tagset.html
# Penn Treebank Tags: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html


treetagger_pt = {

    # Adjectives
    'AQ0': 'ADJ',
    'AQA': 'ADJ',
    'AQC': 'ADJ',
    'AQS': 'ADJ',
    'AO0': 'ADJ',
    'AOA': 'ADJ',
    'AOC': 'ADJ',
    'AOS': 'ADJ',
    'A00': 'ADJ',
    'A0C': 'ADJ',
    'A0S': 'ADJ',
}


# Collapse part of speech by first char of portuguese tagset
# Make tags sorta match the Penn Treebank Tags
def maptagsimple_pt(tag):

    tagset = {
        'A': 'JJ',    # Adjective
        'R': 'RB',    # Adverb
        'D': 'DT',    # Determinate
        'N': 'N',     # Noun
        'V': 'VB',    # Verb
        'P': 'PR',    # Pronoun
        'C': 'CC',    # Conjunction
        'I': 'UH',    # Interjection
        'S': 'IN',    # Preposition
        'F': 'PUNC',  # Punctuation
        'Z': 'NUM'    # Figures/Numbers
    }

    return tagset.get(tag[0], 'UNK')  # Just in case we get a bad POS