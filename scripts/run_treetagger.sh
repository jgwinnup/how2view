#!/bin/sh

# Run Treetagger

TREETAGGER_HOME=/tmpssd2/dev/treetagger
# -quiet
TREETAGGER_FLAGS="-token -lemma -no-unknown -quiet -sgml -eos-tag \"</s>\""
TREETAGGER_PARAM=$TREETAGGER_HOME/lib/portuguese.par
TREETAGGER=$TREETAGGER_HOME/bin/tree-tagger
TOKENIZER=$TREETAGGER_HOME/cmd/utf8-tokenize.perl

#| awk '{if (($1=="</s>")||($3=="@card@")||($3=="@ord")||($3==".")||($3=="?")||(tolower($3)==tolower($1))) {print $1} else {print $3}}' \
sed -e 's/ /\n/g' -e 's/$/\n<\/s>\n/' \
  | $TOKENIZER \
  | $TREETAGGER $TREETAGGER_PARAM $TREETAGGER_FLAGS \
  | awk '{if ($1=="</s>") {print $1} else {print $1 "_" $2}}' \
  | tr '\n' ' ' \
  | sed 's/<\/s> /\n/g'