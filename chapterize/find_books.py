import os
import nltk
import math
import collections
from collections import OrderedDict
from operator import itemgetter
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from chapterize_all import NoHeadlinesException
chapters_dir = '/home/lgafurova/Documents/projects/title generation/chapterize/chapterize/books/'

def getContent(filename):
    with open(filename, errors='ignore') as f:
        contents = f.read()
    return contents.split('\n')

def getHeadings(filename):
    # Form 1: Chapter I, Chapter 1, Chapter the First, CHAPTER 1
    # Ways of enumerating chapters, e.g.
    lines = getContent(filename)
    arabicNumerals = '\d+'
    romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
    numberWordsByTens = ['twenty', 'thirty', 'forty', 'fifty', 'sixty',
                         'seventy', 'eighty', 'ninety']
    numberWords = ['one', 'two', 'three', 'four', 'five', 'six',
                   'seven', 'eight', 'nine', 'ten', 'eleven',
                   'twelve', 'thirteen', 'fourteen', 'fifteen',
                   'sixteen', 'seventeen', 'eighteen', 'nineteen'] + numberWordsByTens
    numberWordsPat = '(' + '|'.join(numberWords) + ')'
    ordinalNumberWordsByTens = ['twentieth', 'thirtieth', 'fortieth', 'fiftieth',
                                'sixtieth', 'seventieth', 'eightieth', 'ninetieth'] + \
                               numberWordsByTens
    ordinalNumberWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth',
                          'seventh', 'eighth', 'ninth', 'twelfth', 'last'] + \
                         [numberWord + 'th' for numberWord in numberWords] + ordinalNumberWordsByTens
    ordinalsPat = '(the )?(' + '|'.join(ordinalNumberWords) + ')'
    enumeratorsList = [arabicNumerals, romanNumerals, numberWordsPat, ordinalsPat]
    enumerators = '(' + '|'.join(enumeratorsList) + ')'
    form1 = 'chapter ' + enumerators

    # Form 2: II. The Mail
    enumerators = romanNumerals
    separators = '(\. | )'
    titleCase = '[A-Z][a-z]'
    form2 = enumerators + separators + titleCase

    # Form 3: II. THE OPEN ROAD
    enumerators = romanNumerals
    separators = '(\. )'
    titleCase = '[A-Z][A-Z]'
    form3 = enumerators + separators + titleCase

    # Form 4: a number on its own, e.g. 8, VIII
    arabicNumerals = '^\d+\.?$'
    romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.?$'
    enumeratorsList = [arabicNumerals, romanNumerals]
    enumerators = '(' + '|'.join(enumeratorsList) + ')'
    form4 = enumerators

    pat = re.compile(form1, re.IGNORECASE)
    # This one is case-sensitive.
    pat2 = re.compile('(%s|%s|%s)' % (form2, form3, form4))

    # TODO: can't use .index() since not all lines are unique.

    headings = []
    for i, line in enumerate(lines):
        if pat.match(line) is not None:
            headings.append(i)
            print('')
        if pat2.match(line) is not None:
            headings.append(i)
            print('')


    if len(headings) < 3:
        raise NoHeadlinesException('Detected fewer than three chapters')

    print('headings')

    return headings


for root, dirs, files in os.walk(chapters_dir):
    print('root = '+root)
    print('files = '+str(files))
    for filename in files:
        headings= []
        try:
            headings = getHeadings(root + '/'+filename)
        except NoHeadlinesException as ex:
            continue
        print('')
