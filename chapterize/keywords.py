import os
import nltk
import math
import collections
from collections import OrderedDict
from operator import itemgetter
import re
from nltk.tokenize import sent_tokenize, word_tokenize

from nltk.corpus import stopwords
word_list = stopwords.words('english')

chapters_dir = 'out'
dataset_filename = 'data.txt'

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


data_dict = dict()
corpus = []
for root, dirs, files in os.walk(chapters_dir):
    print(files)
    for file in files:
        text = [line for line in open(root + '/'+file)]
        print ('title = ' + text[0])
        # сразу находить ключевые слова и записывать
        #print ('text = '+ str(text[1:]))
        plain_text = ''.join(text[1:])
        data_dict[plain_text] = text[0]
        corpus.append(plain_text)

for i in range(len(corpus)):
    corpus[i] = delete_stop_words(pre_process(corpus[i]))
#data_dict {text(key) : chapter_name(value)}
for text, chapter_name in data_dict.items():
    corpus_keywords = get_TF_IDF(corpus)
for doc_tf_idf in corpus_keywords:
    i = 0
    for key, val in doc_tf_idf:
        if i == 10:
            print('\n\n')
            break
        #print (str(i) + ' -- ' + str(key)+ '  '+str(val))
        print(str(key), sep=' ')
        i+=1
