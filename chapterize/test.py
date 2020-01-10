import os
import nltk
import math
import collections
from collections import OrderedDict
from operator import itemgetter
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import pandas as pd


from nltk.corpus import stopwords
word_list = stopwords.words('english')

chapters_dir = 'out'

def delete_stop_words(text):
    words = word_tokenize(text)
    clean_words = [  word for word in words if word not in word_list ]
    return ' '.join(clean_words)


def pre_process(text):
    text = str(text)
    # lowercase
    text = text.lower()

    # remove tags
    text = re.sub("<!--?.*?-->", "", text)

    # remove special characters and digits
    text = re.sub("(\\d\\n|\\W)+", " ", text)
    return text

def get_tokens_from_text(text):
    tokens = [word_tokenize(sent) for sent in sent_tokenize(text)]
    vocab = []
    for sent in tokens:
        vocab = vocab + sent
    return vocab

# count TF
def count_TF(text):
    # term frequency = quantity of word in text / len(text)
    tokens_list =get_tokens_from_text(text)
    tf_text = collections.Counter(tokens_list)
    vocab_len = float(len(tf_text))
    for i in tf_text:
        tf_text[i] =  tf_text[i] / vocab_len
    return tf_text

def count_IDF(word, corpus):
    # idf = len(corpus) / количество документов, в которых есть слово
    # получаем IDF для для переданного термина
    len_corpus = len(corpus)
    term_doc_freq = sum([1.0 for i in corpus if word in i])
    return math.log10(len_corpus / term_doc_freq)

def get_TF_IDF(corpus):
    # считаем tf-idf как произведение признаков TF  и IDF
    documents_list  = []
    for text in corpus:
        tf_text = count_TF(text)
        tf_idf_text = {}
        for word in tf_text:
            tf_idf_text[word] = tf_text[word]*count_IDF(word, corpus)
        documents_list.append(sorted(tf_idf_text.items(), key = itemgetter(1), reverse = True ))
    return documents_list


for root, dirs, files in os.walk(chapters_dir):
    print(files)
    corpus = []
    titles = []
    for file in files:
        text = [line for line in open(root + '/'+file)]
        titles.append(text[0])
        plain_text = delete_stop_words(pre_process(''.join(text[1:])))
        corpus.append(plain_text)
    key_words = get_TF_IDF(corpus)
    for j in range(len(titles)):
        key_words_str = ''
        for i in range(10):
            key_words_str = key_words_str + ' ' + key_words[j][i][0]
        # удалить подстроку, обозначающую, что это глава  (CHAPTER / римские цифры и тд)  НА ЭТАПЕ ЧАПТЕРИЗАЦИИ
        print(titles[j] + ' -- ' + key_words_str + '\n')


