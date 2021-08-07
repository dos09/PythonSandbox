"""
works only for one specific website ...

1. View Page Source -> copy all -> paste in file
2. Run this script with the file from 1.

python3 searching_for_horror_movies.py --file-name XXX --movie-type ужас
"""
import argparse
import os
import re
from html.parser import HTMLParser
from collections import Counter
import json


class MyHTMLParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_tag = None
        self.movies = set()
    
    def handle_starttag(self, tag, attrs):
        self.cur_tag = tag

    def handle_endtag(self, tag):
        self.cur_tag = None

    def handle_data(self, data):
        if self.cur_tag == 'p':
            self.movies.add(data)


def read_cli():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--file-name', required=True,
                        help='File with pasted webpage(s) source code')
    parser.add_argument('--movie-type', default='Ужас',
                        help='Например: Ужас, Комедия...')
    args = parser.parse_args()
    if not os.path.isfile(args.file_name):
        raise ValueError('--file-name must be valid file')
    
    return args


def read_file(file_name):
    with open(file_name) as fin:
        return fin.read()


def get_movies_for_type(data, movie_type):
    print('Substring "%s" found %s time(s)' % 
          (movie_type, data.upper().count(movie_type.upper())))
    html_parser = MyHTMLParser()
    # page in URL is 0-based
    # page in edit box is 1-based
    page_counter = Counter()
    regex_page_num = re.compile(r"<input type=text name=page value='(\d+)'")
    for m in regex_page_num.finditer(data):
        page_num = int(m.group(1))
        page_counter[page_num] += 1
        
    regex_movie = re.compile('<br>%s.+?((?:<p>|<p style).+?</p>)' % movie_type,
                       flags=re.IGNORECASE | re.DOTALL)
    print('Using regex: "%s"' % regex_movie)
    for m in regex_movie.finditer(data):
        p_tag = m.group(1)
        html_parser.feed(p_tag)
    
    html_parser.close()  # flush
    for k, v in page_counter.items():
        # there are 2 edit boxes for entering page (top and bottom)
        val = int(v / 2)
        if val != 1:
            # copy/paste failed and pasted the last page twice
            raise Exception('Page processed more than once: "%s" = %s' % 
                            (k, val))
        page_counter[k] = val
        
    print('Pages processed: %s' % 
          json.dumps(page_counter, indent=4, sort_keys=True))
    return sorted(html_parser.movies)


def run():
    args = read_cli()
    print('Data file with source code: %s' % args.file_name)
    print('Search for movies with type: %s' % args.movie_type)
    file_data = read_file(args.file_name)
    movies = get_movies_for_type(file_data, args.movie_type)
    print('Movies found: %s' % len(movies))        
    for movie in movies:
        print(movie)
    

if __name__ == '__main__':
    run()
# test1