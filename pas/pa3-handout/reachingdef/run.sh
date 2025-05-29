#!/bin/bash

# Modify this script to execute your program on input file $INPUT and output
# file $OUTPUT with command `./run.sh $INPUT $OUTPUT`
INPUT=$1
OUTPUT=$2

python3 reachingdef.py "$INPUT" "$OUTPUT"
