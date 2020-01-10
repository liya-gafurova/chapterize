import os
from chapterize import *

working_dir =  './books/'
out_dir = 'out'
files = os.listdir(working_dir)
for file_name in files:
    print(file_name)
    try:
        cli(book = working_dir+'/'+file_name,out_dir = out_dir)
    except Exception as ex:
        if isinstance(ex, NoHeadlinesException):
            print('no chaters -- raised exception')
            continue
    print('iter_fin')
print('final')

for root, dirs, files in os.walk(out_dir):
    print('root = {}  dirs = {} files = {}'.format(root, dirs, files))