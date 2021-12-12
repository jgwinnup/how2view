#!/bin/bash

# Cuts MT output from annotated.out files
# Columns:
# 1. line number
# 2. 

cut -d$'\t' -f1-4 < $1 > $2
