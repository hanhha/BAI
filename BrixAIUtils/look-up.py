#!/usr/bin/env python3
from argparse import ArgumentParser as ArgParser
import DictLookup 

ap = ArgParser()
ap.add_argument ('-w', '--word', default = '', help = 'English word')
ap.add_argument ('-f', '--file', default = '', help = 'List of words in file, each word per line')
ap.add_argument ('-s', '--sort_unique', action='store_true', help = 'List of words in file, each word per line')
args = ap.parse_args ()
word = args.word
filename = args.file
sortu = args.sort_unique

word_list = []
if word is not '':
    word_list.extend([word])

if filename is not '':
    with open(filename, "r") as f:
        for line in f:
            words = [w.strip() for w in line.split(',')]
            word_list.extend(words)

if sortu is True:
    word_list = sorted(set(word_list))

for w in word_list:
    print (w)
    print ('=============')
    pron, desc, rela = DictLookup.lookup (w)
    print (pron)
    print (desc)
    for s in rela: print (s)
